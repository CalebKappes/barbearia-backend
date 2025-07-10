# core/admin.py

from django.contrib import admin
from .models import Servico, Profissional, Cliente, Agendamento

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'duracao')
    search_fields = ('nome',)

@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'celular', 'usuario')
    search_fields = ('nome',)

# ### CLASSE MODIFICADA ABAIXO ###
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """ Customização do Admin para o modelo Cliente. """
    # Adicione 'usuario' ao início da lista para que ele apareça como a primeira coluna
    list_display = ('usuario', 'nome', 'celular', 'email')
    search_fields = ('nome', 'celular', 'usuario__username') # Permite buscar pelo nome de usuário

# (A classe AgendamentoAdmin continua igual)
@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'servico', 'profissional', 'data_hora_inicio', 'status')
    list_filter = ('status', 'profissional', 'data_hora_inicio')
    search_fields = ('cliente__nome', 'servico__nome')