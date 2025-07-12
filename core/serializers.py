# core/serializers.py

from rest_framework import serializers
from .models import Servico, Profissional, Cliente, Agendamento
from django.contrib.auth.models import User
# Adicione a importação para o nosso novo serializer de token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# --- SERIALIZERS EXISTENTES ---
class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = '__all__'

class ProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profissional
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = '__all__'
        read_only_fields = ('cliente',)

class UserRegistrationSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(write_only=True)
    celular = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'nome', 'celular')

    def create(self, validated_data):
        nome_cliente = validated_data.pop('nome')
        celular_cliente = validated_data.pop('celular')
        user = User.objects.create_user(**validated_data)
        Cliente.objects.create(
            usuario=user,
            nome=nome_cliente,
            celular=celular_cliente,
            email=user.email
        )
        return user

# --- NOVA CLASSE QUE ESTAVA A FALTAR ---
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Adiciona informações customizadas ao token
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        return token