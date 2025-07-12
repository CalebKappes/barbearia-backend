# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServicoViewSet,
    ProfissionalViewSet,
    ClienteViewSet,
    AgendamentoViewSet,
    UserRegistrationView  # A view de cadastro
)

router = DefaultRouter()
router.register(r'servicos', ServicoViewSet, basename='servico')
router.register(r'profissionais', ProfissionalViewSet, basename='profissional')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamento')

# A lista de URLs do nosso app 'core'
urlpatterns = [
    # URLs geradas automaticamente pelo router (servicos, profissionais, etc.)
    path('', include(router.urls)),

    # URL para o nosso endpoint de cadastro
    path('register/', UserRegistrationView.as_view(), name='user-register'),
]