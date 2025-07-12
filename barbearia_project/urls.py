# barbearia_project/urls.py

from django.contrib import admin
from django.urls import path, include

# Importações para o nosso login com token customizado
from core.views import MyTokenObtainPairView
# Importação para o refresh do token
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Rotas que já tínhamos
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),  # Aponta para o outro arquivo urls.py

    # Rotas de Autenticação
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]