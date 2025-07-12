# core/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminUserOrReadOnly(BasePermission):
    """
    Permissão customizada que permite acesso de leitura a qualquer um,
    mas apenas administradores (is_staff=True) podem escrever.
    """
    def has_permission(self, request, view):
        # Se o método for seguro (GET, HEAD, OPTIONS), permite o acesso.
        if request.method in SAFE_METHODS:
            return True

        # Para outros métodos (POST, PUT, DELETE), verifica se o usuário
        # está autenticado E se ele é um membro da equipe (staff).
        return bool(request.user and request.user.is_staff)