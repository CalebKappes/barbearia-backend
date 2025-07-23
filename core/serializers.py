# core/serializers.py

from rest_framework import serializers
from datetime import timedelta
# CORREÇÃO: Importamos o módulo 'models' inteiro para evitar importações circulares.
from . import models
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# --- SERIALIZERS ATUALIZADOS ---

class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para o nosso modelo de usuário customizado.
    """
    class Meta:
        # Apontamos para o modelo através do módulo.
        model = models.Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ServicoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Servico.
    """
    class Meta:
        model = models.Servico
        fields = '__all__'


class BarbeiroSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Barbeiro.
    """
    class Meta:
        model = models.Barbeiro
        fields = '__all__'


class AgendamentoSerializer(serializers.ModelSerializer):
    # As relações aninhadas já usam as classes de serializer definidas acima, o que está correto.
    servico = ServicoSerializer(read_only=True)
    barbeiro = BarbeiroSerializer(read_only=True)

    # Os querysets para os campos de escrita também precisam usar o novo padrão de importação.
    servico_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Servico.objects.all(), source='servico', write_only=True, label="Serviço"
    )
    barbeiro_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Barbeiro.objects.all(), source='barbeiro', write_only=True, label="Barbeiro"
    )

    class Meta:
        model = models.Agendamento
        fields = [
            'id', 'cliente', 'data_agendamento', 'confirmado',
            'servico', 'barbeiro', 'servico_id', 'barbeiro_id'
        ]
        read_only_fields = ['cliente']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para o registo de novos usuários.
    """
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = models.Usuario
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        # Validação para garantir que as duas senhas são iguais
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "As senhas não correspondem."})
        return data

    def create(self, validated_data):
        # Remove o campo 'password2' que não faz parte do modelo Usuario
        validated_data.pop('password2')
        # Cria o usuário usando o método create_user que já encripta a senha
        user = models.Usuario.objects.create_user(**validated_data)
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer para obter o token de autenticação.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Adiciona informações customizadas ao token
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        return token
