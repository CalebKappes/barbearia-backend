# core/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUserOrReadOnly(BasePermission):
    """
    Permissão customizada que permite acesso de leitura a qualquer um autenticado,
    mas apenas administradores (is_staff=True) podem escrever.
    """

    def has_permission(self, request, view):
        # Se o método for seguro (GET, HEAD, OPTIONS), permite o acesso para qualquer usuário logado.
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)

        # Para outros métodos (POST, PUT, DELETE), exige que seja administrador.
        return bool(request.user and request.user.is_staff)