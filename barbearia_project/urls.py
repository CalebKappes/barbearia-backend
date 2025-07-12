# barbearia_project/urls.py

from django.contrib import admin
from django.urls import path, include

from core.views import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),

    # Rotas de Autenticação por Token para o nosso App React
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Rota de autenticação por sessão para a API Navegável (para testes)
    path('api-auth/', include('rest_framework.urls')),
]