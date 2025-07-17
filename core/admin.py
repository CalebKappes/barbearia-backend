# core/admin.py

from django.contrib import admin
# Importando o novo modelo BloqueioDeAgenda
from .models import Usuario, Servico, Barbeiro, Agendamento, BloqueioDeAgenda

admin.site.register(Usuario)
admin.site.register(Servico)
admin.site.register(Barbeiro)
admin.site.register(Agendamento)
# Registrando o novo modelo
admin.site.register(BloqueioDeAgenda)