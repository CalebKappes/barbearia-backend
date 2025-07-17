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

# Cole esta versão completa da classe Agendamento no seu models.py

# Cole esta versão completa da classe Agendamento no seu models.py

class Agendamento(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="agendamentos")
    data_agendamento = models.DateTimeField()
    confirmado = models.BooleanField(default=False)
    servico = models.ForeignKey(Servico, on_delete=models.SET_NULL, null=True, blank=True)
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        super().clean()
        if not self.barbeiro or not self.servico or not self.data_agendamento:
            return

        # Calcula o início e o fim do horário do agendamento proposto
        inicio_agendamento = self.data_agendamento
        duracao_servico = timedelta(minutes=self.servico.duracao_em_minutos)
        fim_agendamento = inicio_agendamento + duracao_servico

        # --- LÓGICA DE VALIDAÇÃO ATUALIZADA ---

        # 1. Validação do horário de trabalho
        if not (self.barbeiro.horario_inicio_trabalho <= inicio_agendamento.time() and
                fim_agendamento.time() <= self.barbeiro.horario_fim_trabalho):
            raise ValidationError(
                {'data_agendamento': "O horário do serviço (início e fim) está fora do expediente do barbeiro."})

        # 2. Validação do horário de almoço
        almoco_inicio = self.barbeiro.horario_inicio_almoco
        almoco_fim = self.barbeiro.horario_fim_almoco
        if (inicio_agendamento.time() < almoco_fim and fim_agendamento.time() > almoco_inicio):
            raise ValidationError({'data_agendamento': "O horário solicitado conflita com o período de almoço."})

        # 3. Validação de BLOQUEIOS DE AGENDA (a nova lógica)
        bloqueios_do_dia = BloqueioDeAgenda.objects.filter(
            barbeiro=self.barbeiro,
            data=inicio_agendamento.date()
        )
        for bloqueio in bloqueios_do_dia:
            if (inicio_agendamento.time() < bloqueio.hora_fim and fim_agendamento.time() > bloqueio.hora_inicio):
                raise ValidationError(
                    {'data_agendamento': "O horário solicitado conflita com um período de bloqueio na agenda."})

        # 4. Validação de conflito com outros AGENDAMENTOS
        agendamentos_conflitantes = Agendamento.objects.filter(
            barbeiro=self.barbeiro,
            data_agendamento__date=inicio_agendamento.date()
        ).exclude(pk=self.pk)

        for agendamento_existente in agendamentos_conflitantes:
            inicio_existente = agendamento_existente.data_agendamento
            fim_existente = inicio_existente + timedelta(minutes=agendamento_existente.servico.duracao_em_minutos)

            if inicio_agendamento < fim_existente and fim_agendamento > inicio_existente:
                raise ValidationError(f"Conflito de horário. Já existe um agendamento neste período.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        cliente_nome = self.cliente.get_full_name() or self.cliente.username
        servico_nome = self.servico.nome if self.servico else "Serviço não definido"
        return f"{servico_nome} para {cliente_nome} em {self.data_agendamento.strftime('%d/%m/%Y às %H:%M')}"

# Adicionar esta nova classe no models.py (e apagar a classe DiaDeFolga)

class BloqueioDeAgenda(models.Model):
    """
    Modelo para registrar períodos de ausência (folgas, reuniões, etc.)
    em que um barbeiro não estará disponível.
    """
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE, related_name="bloqueios")
    data = models.DateField(help_text="O dia do bloqueio.")
    hora_inicio = models.TimeField(help_text="Horário de início do bloqueio.")
    hora_fim = models.TimeField(help_text="Horário de fim do bloqueio.")
    motivo = models.CharField(max_length=200, blank=True, null=True, help_text="Motivo da ausência (opcional).")

    class Meta:
        ordering = ['data', 'hora_inicio'] # Ordena os bloqueios por data e hora

    def __str__(self):
        return f"Bloqueio de {self.barbeiro.nome} em {self.data.strftime('%d/%m/%Y')} das {self.hora_inicio.strftime('%H:%M')} às {self.hora_fim.strftime('%H:%M')}"