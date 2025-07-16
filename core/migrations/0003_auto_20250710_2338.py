# Este é o conteúdo do seu novo arquivo de migração (ex: 0003_auto_....py)

from django.db import migrations
from decouple import config
# Esta função define a ação que queremos executar: criar um superusuário.
def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    # Use seus dados aqui!
    User.objects.create_superuser(
        username='Caleb',
        email='calebekappes2@gmail.com',
        password='spfc16011995'
    )

class Migration(migrations.Migration):

    # Esta linha diz ao Django que esta migração depende da anterior.
    # Verifique na sua pasta 'migrations' se o arquivo anterior é o '0002'. Se for, está correto.
    dependencies = [
        ('core', '0002_cliente_usuario'),
    ]

    # Aqui, dizemos ao Django para executar nossa função 'create_superuser'.
    operations = [
        migrations.RunPython(create_superuser),
    ]