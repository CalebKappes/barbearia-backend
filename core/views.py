# core/views.py

# --- BLOCO DE IMPORTS ATUALIZADO ---
from django.utils import timezone
from rest_framework import viewsets, status, generics  # Adicionamos 'generics'
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from datetime import datetime, time, timedelta
from django.contrib.auth.models import User  # Adicionamos a importação do User

from .models import Servico, Profissional, Cliente, Agendamento
# Adicionamos a importação do novo serializer
from .serializers import (
    ServicoSerializer,
    ProfissionalSerializer,
    ClienteSerializer,
    AgendamentoSerializer,
    UserRegistrationSerializer
)


# --- SUAS VIEWS ATUAIS (CONTINUAM IGUAIS) ---
class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    serializer_class = ProfissionalSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

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
        horario_fim_dia = datetime.combine(data, horario_fim_trabalho)

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
    permission_classes = [IsAuthenticated]  # Alterado para proteger dados de clientes


class AgendamentoViewSet(viewsets.ModelViewSet):
    serializer_class = AgendamentoSerializer
    permission_classes = [IsAuthenticated]
    queryset = Agendamento.objects.all()

    def get_queryset(self):
        usuario_logado = self.request.user
        if usuario_logado.is_authenticated:
            return self.queryset.filter(cliente__usuario=usuario_logado)
        return self.queryset.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cliente = request.user.cliente
            serializer.save(cliente=cliente)
        except AttributeError:
            return Response(
                {"detail": "Este usuário não possui um perfil de cliente associado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# --- NOVA VIEW PARA ADICIONAR AO FINAL DO ARQUIVO ---
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)  # Permite que qualquer um se cadastre
    serializer_class = UserRegistrationSerializer