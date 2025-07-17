from django.core.exceptions import ValidationError
from datetime import timedelta
from datetime import time
from django.db import models
from django.contrib.auth.models import AbstractUser


# Modelo de Usuário - A base para clientes e, futuramente, para os próprios barbeiros.
class Usuario(AbstractUser):
    # Podemos adicionar campos extras aqui no futuro, como telefone ou foto de perfil.
    # Por enquanto, vamos usar o padrão do Django.
    pass


# --- NOSSOS NOVOS MODELOS ---

# Modelo para os SERVIÇOS que a barbearia oferece.
class Servico(models.Model):
    nome = models.CharField(max_length=100, help_text="Ex: Corte de Cabelo")
    descricao = models.TextField(blank=True, null=True, help_text="Uma breve descrição do serviço (opcional).")
    preco = models.DecimalField(max_digits=7, decimal_places=2, help_text="Preço do serviço, ex: 50.00")
    duracao_em_minutos = models.IntegerField(help_text="Duração aproximada do serviço em minutos.")

    # Isso ajuda a mostrar um nome legível no painel de admin do Django
    def __str__(self):
        return self.nome


# Modelo para os Barbeiros (com horários de trabalho)
class Barbeiro(models.Model):
    nome = models.CharField(max_length=100)

    # --- NOSSOS NOVOS CAMPOS DE HORÁRIO ---
    # Usamos TimeField para guardar apenas a hora, sem a data.
    # Definimos um valor padrão para facilitar a criação de novos barbeiros.
    horario_inicio_trabalho = models.TimeField(default=time(9, 0))  # Padrão 09:00
    horario_fim_trabalho = models.TimeField(default=time(19, 0)) # Padrão 19:00
    horario_inicio_almoco = models.TimeField(default=time(12, 0))# Padrão 12:00
    horario_fim_almoco = models.TimeField(default=time(14, 0)) # Padrão 14:00

    def __str__(self):
        return self.nome


# core/models.py

class Agendamento(models.Model):
    # --- Seus campos existentes (sem alteração) ---
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="agendamentos")
    data_agendamento = models.DateTimeField()
    confirmado = models.BooleanField(default=False)
    servico = models.ForeignKey(Servico, on_delete=models.SET_NULL, null=True, blank=True)
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.SET_NULL, null=True, blank=True)

    # --- Nosso método de validação (sem alteração) ---
    def clean(self):
        super().clean()
        if not self.barbeiro or not self.servico or not self.data_agendamento:
            return

        horario_agendamento = self.data_agendamento.time()

        if not (self.barbeiro.horario_inicio_trabalho <= horario_agendamento < self.barbeiro.horario_fim_trabalho):
            raise ValidationError({'data_agendamento': "O horário solicitado está fora do expediente do barbeiro."})

        if (self.barbeiro.horario_inicio_almoco <= horario_agendamento < self.barbeiro.horario_fim_almoco):
            raise ValidationError({'data_agendamento': "O horário solicitado está no período de almoço do barbeiro."})

        duracao_servico = timedelta(minutes=self.servico.duracao_em_minutos)
        fim_agendamento = self.data_agendamento + duracao_servico

        agendamentos_conflitantes = Agendamento.objects.filter(
            barbeiro=self.barbeiro,
            data_agendamento__date=self.data_agendamento.date()
        ).exclude(pk=self.pk)

        for agendamento_existente in agendamentos_conflitantes:
            inicio_existente = agendamento_existente.data_agendamento
            fim_existente = inicio_existente + timedelta(minutes=agendamento_existente.servico.duracao_em_minutos)

            if self.data_agendamento < fim_existente and fim_agendamento > inicio_existente:
                raise ValidationError(f"Conflito de horário. Já existe um agendamento neste período.")

    # --- O MÉTODO QUE FALTAVA ---
    # Adicionamos este método para forçar a validação a rodar sempre
    def save(self, *args, **kwargs):
        self.full_clean()  # Chama o método .clean() e todas as outras validações do modelo
        super().save(*args, **kwargs)  # Se tudo estiver ok, salva o objeto

    # --- Método __str__ (sem alteração) ---
    def __str__(self):
        cliente_nome = self.cliente.get_full_name() or self.cliente.username
        servico_nome = self.servico.nome if self.servico else "Serviço não definido"
        return f"{servico_nome} para {cliente_nome} em {self.data_agendamento.strftime('%d/%m/%Y às %H:%M')}"