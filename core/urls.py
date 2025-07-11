# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Adicione a UserRegistrationView à importação
from .views import (
    ServicoViewSet,
    ProfissionalViewSet,
    ClienteViewSet,
    AgendamentoViewSet,
    UserRegistrationView
)

# O router continua o mesmo
router = DefaultRouter()
router.register(r'servicos', ServicoViewSet, basename='servico')
router.register(r'profissionais', ProfissionalViewSet, basename='profissional')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamento')

# Adicionamos a nova URL à lista urlpatterns
urlpatterns = [
    path('', include(router.urls)),
    # Esta é a nova linha para o nosso endpoint de cadastro
    path('register/', UserRegistrationView.as_view(), name='user-register'),
]