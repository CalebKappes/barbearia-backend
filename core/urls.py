# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# --- IMPORTS CORRIGIDOS ---
# Importando as ViewSets com os nomes corretos do nosso views.py refatorado
from .views import (
    ServicoViewSet,
    BarbeiroViewSet,  # Corrigido de ProfissionalViewSet
    UsuarioViewSet,  # Corrigido de ClienteViewSet
    AgendamentoViewSet,
    UserRegistrationView,
    AdminAgendamentoViewSet
)

# Criação do router padrão do Django Rest Framework
router = DefaultRouter()

# --- REGISTROS DO ROUTER CORRIGIDOS ---
# Registrando as rotas da API com os nomes e ViewSets corretos
# O router cria automaticamente as rotas de listagem, detalhe, criação, etc.
router.register(r'servicos', ServicoViewSet, basename='servico')
router.register(r'barbeiros', BarbeiroViewSet, basename='barbeiro')  # Corrigido
router.register(r'usuarios', UsuarioViewSet, basename='usuario')  # Corrigido
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamento')
router.register(r'admin/agenda', AdminAgendamentoViewSet, basename='admin-agenda')

# Lista final de URLs da nossa API 'core'
urlpatterns = [
    # Rota para o cadastro de novos usuários (ex: /api/register/)
    path('register/', UserRegistrationView.as_view(), name='user-register'),

    # Inclui todas as rotas que registramos no router acima (ex: /api/servicos/, /api/barbeiros/)
    # Esta linha deve vir DEPOIS de rotas específicas como 'register/'
    path('', include(router.urls)),
]