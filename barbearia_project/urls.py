# barbearia_project/urls.py
from django.contrib import admin
from django.urls import path, include

# Adicione estas importações da biblioteca JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),

    # Remova a linha 'api-auth/' se ela ainda existir.

    # ADICIONE ESTAS DUAS NOVAS LINHAS:
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
]