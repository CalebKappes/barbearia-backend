# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServicoViewSet, ProfissionalViewSet, ClienteViewSet, AgendamentoViewSet

# Cria um roteador para registrar nossos ViewSets
router = DefaultRouter()
router.register(r'servicos', ServicoViewSet)
router.register(r'profissionais', ProfissionalViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'agendamentos', AgendamentoViewSet)

# As URLs da API são agora determinadas automaticamente pelo roteador
urlpatterns = [
    path('', include(router.urls)),
]