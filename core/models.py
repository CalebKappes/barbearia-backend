# core/models.py

from django.db import models
from django.conf import settings  # Usaremos para vincular o profissional ao usuário do Django
from django.core.exceptions import ValidationError
import datetime


# Modelo para os serviços oferecidos pela barbearia
class Servico(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Serviço")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    preco = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Preço")
    duracao = models.DurationField(
        verbose_name="Duração do Serviço",
        help_text="Formato: HH:MM:SS (ex: 01:00:00 para 1 hora)"
    )

    def __str__(self):
        return self.nome


# Modelo para os profissionais (barbeiros)
class Profissional(models.Model):
    # Vincula o profissional a um usuário do sistema para login.
    # Se o profissional for deletado, o usuário associado NÃO será.
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    nome = models.CharField(max_length=100, verbose_name="Nome Completo")
    celular = models.CharField(max_length=15, blank=True, null=True, verbose_name="Celular")

    def __str__(self):
        return self.nome


# Modelo para os clientes da barbearia
class Cliente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cliente',
        # Adicione estas duas linhas para tornar o campo opcional:
        null=True,
        blank=True)
    nome = models.CharField(max_length=100, verbose_name="Nome Completo")
    celular = models.CharField(max_length=15, unique=True, verbose_name="Celular (será o login)")
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.celular})"


# core/models.py
# (As outras classes: Servico, Profissional, Cliente continuam iguais acima)

# Modelo para os agendamentos (VERSÃO CORRIGIDA)
class Agendamento(models.Model):
    STATUS_CHOICES = [
        ('AGD', 'Agendado'),
        ('CNF', 'Confirmado'),
        ('CON', 'Concluído'),
        ('CAN', 'Cancelado'),
    ]

    servico = models.ForeignKey(Servico, on_delete=models.CASCADE, verbose_name="Serviço")
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, verbose_name="Profissional")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    data_hora_inicio = models.DateTimeField(verbose_name="Início do Atendimento")
    data_hora_fim = models.DateTimeField(verbose_name="Fim do Atendimento", editable=False) # Calculado automaticamente
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='AGD', verbose_name="Status")

    def save(self, *args, **kwargs):
        # Calcula a hora de término automaticamente ao salvar
        if self.data_hora_inicio and self.servico:
            self.data_hora_fim = self.data_hora_inicio + self.servico.duracao
        super().save(*args, **kwargs)

    # ### MÉTODO CLEAN CORRIGIDO ###
    def clean(self):
        # A validação só executa se os campos essenciais estiverem preenchidos
        if self.profissional and self.data_hora_inicio and self.servico:
            # Calcula o horário de término para a validação
            end_time = self.data_hora_inicio + self.servico.duracao

            # Executa a busca por agendamentos conflitantes
            agendamentos_conflitantes = Agendamento.objects.filter(
                profissional=self.profissional,
                status__in=['AGD', 'CNF', 'CON'],
                data_hora_inicio__lt=end_time,
                data_hora_fim__gt=self.data_hora_inicio,
            ).exclude(pk=self.pk)

            if agendamentos_conflitantes.exists():
                raise ValidationError(f"O profissional {self.profissional} já possui um agendamento neste horário.")

    def __str__(self):
        # Adicionado um 'if' para evitar erros se algum campo estiver vazio durante a criação
        if self.servico and self.profissional and self.cliente and self.data_hora_inicio:
            return f"{self.servico.nome} com {self.profissional.nome} para {self.cliente.nome} em {self.data_hora_inicio.strftime('%d/%m/%Y %H:%M')}"
        return "Novo Agendamento"