from django.contrib import admin
# Importando os modelos com os nomes corretos do nosso novo models.py
from .models import Usuario, Servico, Barbeiro, Agendamento

# Registrando cada modelo no site de administração do Django
# Isso fará com que você possa adicionar/editar/remover
# Serviços, Barbeiros e Agendamentos pelo painel de admin.
admin.site.register(Usuario)
admin.site.register(Servico)
admin.site.register(Barbeiro)
admin.site.register(Agendamento)