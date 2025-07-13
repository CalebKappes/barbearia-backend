# core/management/commands/enviar_lembretes.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from core.models import Agendamento


class Command(BaseCommand):
    help = 'Verifica agendamentos próximos e envia e-mails de lembrete.'

    def handle(self, *args, **options):
        agora = timezone.now()
        # Define o intervalo de tempo: de 55 a 65 minutos a partir de agora
        limite_inferior = agora + timedelta(minutes=55)
        limite_superior = agora + timedelta(minutes=65)

        # Busca os agendamentos que estão no intervalo, com status 'Agendado'
        # e para os quais um lembrete ainda não foi enviado.
        agendamentos_para_lembrar = Agendamento.objects.filter(
            data_hora_inicio__gte=limite_inferior,
            data_hora_inicio__lte=limite_superior,
            status='AGD',
            lembrete_enviado=False
        )

        self.stdout.write(
            f'Verificando agendamentos entre {limite_inferior.strftime("%H:%M")} e {limite_superior.strftime("%H:%M")}')

        if not agendamentos_para_lembrar:
            self.stdout.write(self.style.SUCCESS('Nenhum lembrete para enviar no momento.'))
            return

        total_enviado = 0
        for agendamento in agendamentos_para_lembrar:
            try:
                cliente = agendamento.cliente
                data_formatada = agendamento.data_hora_inicio.strftime('%d/%m/%Y')
                hora_formatada = agendamento.data_hora_inicio.strftime('%H:%M')

                assunto = f"Lembrete de Agendamento - {agendamento.servico.nome}"
                corpo = (
                    f"Olá, {cliente.nome}!\n\n"
                    f"Este é um lembrete do seu agendamento que acontecerá em breve.\n\n"
                    f"Serviço: '{agendamento.servico.nome}' com {agendamento.profissional.nome}\n"
                    f"Data: {data_formatada}\n"
                    f"Horário: {hora_formatada}\n\n"
                    "Até já!\n"
                    "Sherlock Barber"
                )

                email_remetente = settings.SENDGRID_FROM_EMAIL
                email_destinatario = [cliente.email]

                send_mail(assunto, corpo, email_remetente, email_destinatario, fail_silently=False)

                # Marca o lembrete como enviado para não enviar de novo
                agendamento.lembrete_enviado = True
                agendamento.save()
                total_enviado += 1

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Erro ao enviar lembrete para agendamento {agendamento.id}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Total de {total_enviado} lembretes enviados com sucesso!'))
