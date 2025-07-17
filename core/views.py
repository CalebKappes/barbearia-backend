# core/views.py

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from datetime import datetime, time, timedelta
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core import management
from .permissions import IsAdminUserOrReadOnly

# --- IMPORTS CORRIGIDOS ---
from .models import Servico, Barbeiro, Usuario, Agendamento
from .serializers import (
    ServicoSerializer,
    BarbeiroSerializer,
    UsuarioSerializer,
    AgendamentoSerializer,
    UserRegistrationSerializer,
    MyTokenObtainPairSerializer
)


class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class BarbeiroViewSet(viewsets.ModelViewSet):
    queryset = Barbeiro.objects.all()
    serializer_class = BarbeiroSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    # Este método vai dentro da classe BarbeiroViewSet

    @action(detail=True, methods=['get'])
    def horarios_disponiveis(self, request, pk=None):
        data_str = request.query_params.get('data')
        servico_id = request.query_params.get('servico_id')
        if not data_str or not servico_id:
            return Response({"detail": "Os parâmetros 'data' e 'servico_id' são obrigatórios."}, status=400)

        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
            servico = Servico.objects.get(pk=servico_id)
        except (ValueError, Servico.DoesNotExist):
            return Response({"detail": "Data ou serviço inválido."}, status=400)

        barbeiro = self.get_object()
        duracao_servico = timedelta(minutes=servico.duracao_em_minutos)

        # --- LÓGICA REATORADA ---
        # Buscando os horários diretamente do objeto 'barbeiro' do banco de dados!
        # Não usamos mais valores fixos como time(9, 0).
        horario_inicio_trabalho = barbeiro.horario_inicio_trabalho
        horario_fim_trabalho = barbeiro.horario_fim_trabalho
        horario_inicio_almoco = barbeiro.horario_inicio_almoco
        horario_fim_almoco = barbeiro.horario_fim_almoco
        # -------------------------

        intervalo_minimo = timedelta(minutes=15)
        horarios_disponiveis = []

        agendamentos_do_dia = Agendamento.objects.filter(
            barbeiro=barbeiro,
            data_agendamento__date=data
        ).order_by('data_agendamento')

        slot_atual = timezone.make_aware(datetime.combine(data, horario_inicio_trabalho))

        while slot_atual.time() < horario_fim_trabalho:
            slot_fim = slot_atual + duracao_servico
            if slot_fim.time() > horario_fim_trabalho:
                break

            slot_nao_conflita_almoco = not (
                (slot_atual.time() < horario_fim_almoco and slot_fim.time() > horario_inicio_almoco)
            )
            slot_livre = True
            for agendamento in agendamentos_do_dia:
                agendamento_inicio = agendamento.data_agendamento
                agendamento_fim = agendamento_inicio + timedelta(minutes=agendamento.servico.duracao_em_minutos)
                if slot_atual < agendamento_fim and slot_fim > agendamento_inicio:
                    slot_livre = False
                    break

            if slot_nao_conflita_almoco and slot_livre:
                horarios_disponiveis.append(slot_atual.strftime('%H:%M'))

            slot_atual += intervalo_minimo

        return Response(horarios_disponiveis)


class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdminUser]


class AgendamentoViewSet(viewsets.ModelViewSet):
    serializer_class = AgendamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Agendamento.objects.all().order_by('-data_agendamento')
        return Agendamento.objects.filter(cliente=user).order_by('-data_agendamento')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        agendamento = serializer.save(cliente=request.user)

        try:
            data_formatada = agendamento.data_agendamento.strftime('%d/%m/%Y')
            hora_formatada = agendamento.data_agendamento.strftime('%H:%M')
            assunto = f"Confirmação de Agendamento - {agendamento.servico.nome}"
            corpo = f"Olá, {request.user.first_name or request.user.username}!\n\nSeu agendamento para o serviço '{agendamento.servico.nome}' com {agendamento.barbeiro.nome} foi confirmado.\n\nData: {data_formatada}\nHorário: {hora_formatada}\n\nObrigado!"
            send_mail(assunto, corpo, settings.SENDGRID_FROM_EMAIL, [request.user.email], fail_silently=False)
        except Exception as e:
            print(f"ERRO ao enviar e-mail de confirmação: {e}")

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        agendamento = self.get_object()
        if not request.user.is_staff and agendamento.cliente != request.user:
            return Response({'detail': 'Não permitido.'}, status=status.HTTP_403_FORBIDDEN)

        agendamento.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminAgendamentoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AgendamentoSerializer
    permission_classes = [IsAdminUser]
    queryset = Agendamento.objects.all().order_by('-data_agendamento')


class UserRegistrationView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class TriggerRemindersView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        cron_secret = kwargs.get("cron_secret")
        if cron_secret != settings.CRON_SECRET_KEY:
            return Response({"detail": "Não autorizado."}, status=status.HTTP_403_FORBIDDEN)
        try:
            management.call_command('enviar_lembretes')
            return Response({"status": "Lembretes verificados com sucesso."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)