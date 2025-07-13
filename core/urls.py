# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServicoViewSet,
    ProfissionalViewSet,
    ClienteViewSet,
    AgendamentoViewSet,
    UserRegistrationView,
    AdminAgendamentoViewSet  # A view do nosso painel de agenda
)

router = DefaultRouter()
router.register(r'servicos', ServicoViewSet, basename='servico')
router.register(r'profissionais', ProfissionalViewSet, basename='profissional')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamento')
# REMOVA a linha "router.register(r'admin/agenda', ...)" daqui.

# Lista final de URLs
urlpatterns = [
    # Inclui todas as rotas do router (servicos, profissionais, etc.)
    path('', include(router.urls)),

    # Rota de cadastro
    path('register/', UserRegistrationView.as_view(), name='user-register'),

    # ADICIONE A ROTA DA AGENDA DO ADMIN AQUI:
    # Usamos .as_view({'get': 'list'}) porque é uma ReadOnlyModelViewSet que só precisa da ação de listar.
    path('admin/agenda/', AdminAgendamentoViewSet.as_view({'get': 'list'}), name='admin-agenda-list'),
]
