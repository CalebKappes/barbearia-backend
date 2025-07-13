# core/views.py
from django.core.mail import send_mail
from django.conf import settings  # <-- A LINHA QUE FALTAVA PARA CORRIGIR O ERRO
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAdminUserOrReadOnly
from datetime import datetime, time, timedelta
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

from .models import Servico, Profissional, Cliente, Agendamento
from .serializers import (
    ServicoSerializer,
    ProfissionalSerializer,
    ClienteSerializer,
    AgendamentoSerializer,
    UserRegistrationSerializer
)


class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    serializer_class = ProfissionalSerializer
    permission_classes = [IsAdminUserOrReadOnly]

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
        profissional = self.get_object()
        duracao_servico = servico.duracao

        horarios_disponiveis = []
        horario_inicio_trabalho = time(9, 0)
        horario_fim_trabalho = time(18, 0)
        horario_inicio_almoco = time(12, 0)
        horario_fim_almoco = time(13, 0)
        intervalo_minimo = timedelta(minutes=15)

        agendamentos_do_dia = Agendamento.objects.filter(
            profissional=profissional,
            data_hora_inicio__date=data
        ).order_by('data_hora_inicio')

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
                if slot_atual < agendamento.data_hora_fim and slot_fim > agendamento.data_hora_inicio:
                    slot_livre = False
                    break

            if slot_nao_conflita_almoco and slot_livre:
                horarios_disponiveis.append(slot_atual.strftime('%H:%M'))

            slot_atual += intervalo_minimo

        return Response(horarios_disponiveis)


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]


class AgendamentoViewSet(viewsets.ModelViewSet):
    serializer_class = AgendamentoSerializer
    permission_classes = [IsAuthenticated]
    queryset = Agendamento.objects.all()

    def get_queryset(self):
        usuario_logado = self.request.user
        if usuario_logado.is_authenticated:
            return self.queryset.filter(cliente__usuario=usuario_logado).order_by('-data_hora_inicio')
        return self.queryset.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cliente = request.user.cliente
            agendamento = serializer.save(cliente=cliente)

            try:
                data_formatada = agendamento.data_hora_inicio.strftime('%d/%m/%Y')
                hora_formatada = agendamento.data_hora_inicio.strftime('%H:%M')
                assunto = f"Confirmação de Agendamento - {agendamento.servico.nome}"
                corpo = (
                    f"Olá, {cliente.nome}!\n\n"
                    f"Seu agendamento para o serviço '{agendamento.servico.nome}' com o profissional {agendamento.profissional.nome} "
                    f"foi confirmado com sucesso.\n\n"
                    f"Data: {data_formatada}\n"
                    f"Horário: {hora_formatada}\n\n"
                    "Agradecemos a preferência!\n"
                    "Sherlock Barber"
                )
                email_remetente = settings.SENDGRID_FROM_EMAIL
                email_destinatario = [cliente.email]
                send_mail(assunto, corpo, email_remetente, email_destinatario, fail_silently=False)
            except Exception as e:
                print(f"ERRO ao enviar e-mail de confirmação: {e}")

        except AttributeError:
            return Response(
                {"detail": "Este usuário não possui um perfil de cliente associado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        agendamento = self.get_object()
        if agendamento.cliente.usuario != request.user:
            return Response({'detail': 'Você não tem permissão para cancelar este agendamento.'},
                            status=status.HTTP_403_FORBIDDEN)
        agendamento.status = 'CAN'
        agendamento.save()
        serializer = self.get_serializer(agendamento)
        return Response(serializer.data)


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
