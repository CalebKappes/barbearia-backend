# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServicoViewSet,
    ProfissionalViewSet,
    ClienteViewSet,
    AgendamentoViewSet,
    UserRegistrationView,
    TriggerRemindersView  # 1. Adicione a nova view à importação
)

router = DefaultRouter()
router.register(r'servicos', ServicoViewSet, basename='servico')
router.register(r'profissionais', ProfissionalViewSet, basename='profissional')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamento')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user-register'),

    # 2. ADICIONE ESTA NOVA LINHA PARA O CRON JOB:
    # A URL inclui um parâmetro <str:cron_secret> para a nossa chave de segurança
    path('trigger-reminders/<str:cron_secret>/', TriggerRemindersView.as_view(), name='trigger-reminders'),
]
