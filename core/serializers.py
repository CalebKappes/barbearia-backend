# core/serializers.py

from rest_framework import serializers
from datetime import timedelta
# Importando os modelos com os nomes corretos do nosso novo models.py
from .models import Servico, Barbeiro, Usuario, Agendamento
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# --- SERIALIZERS ATUALIZADOS ---

class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para o nosso modelo de usuário customizado.
    """
    class Meta:
        model = Usuario
        # Vamos expor apenas os campos seguros e úteis
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ServicoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Servico. Este já estava correto.
    """
    class Meta:
        model = Servico
        fields = '__all__'


class BarbeiroSerializer(serializers.ModelSerializer):
    """
    CORRIGIDO: Renomeamos de ProfissionalSerializer para BarbeiroSerializer
    e apontamos para o modelo correto 'Barbeiro'.
    """
    class Meta:
        model = Barbeiro
        fields = '__all__'


class AgendamentoSerializer(serializers.ModelSerializer):
    servico = ServicoSerializer(read_only=True)
    barbeiro = BarbeiroSerializer(read_only=True)

    servico_id = serializers.PrimaryKeyRelatedField(
        queryset=Servico.objects.all(), source='servico', write_only=True, label="Serviço"
    )
    barbeiro_id = serializers.PrimaryKeyRelatedField(
        queryset=Barbeiro.objects.all(), source='barbeiro', write_only=True, label="Barbeiro"
    )

    class Meta:
        model = Agendamento
        fields = [
            'id', 'cliente', 'data_agendamento', 'confirmado',
            'servico', 'barbeiro', 'servico_id', 'barbeiro_id'
        ]
        read_only_fields = ['cliente']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    TOTALMENTE REFEITO: Agora este serializer trabalha com o nosso
    modelo 'Usuario' customizado e não mais com o 'Cliente' separado.
    """
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Usuario
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
        user = Usuario.objects.create_user(**validated_data)
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Este já estava correto. Apenas garantimos que ele funciona
    com nosso modelo de usuário.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Adiciona informações customizadas ao token
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        return token