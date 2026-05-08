from django.core.management.base import BaseCommand
from core.scheduler.scheduler import start


class Command(BaseCommand):
    help = 'Inicia o APScheduler'

    def handle(self, *args, **kwargs):

        print('APScheduler iniciado...')

        scheduler = start()

        try:
            # mantém o processo vivo
            import time

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            scheduler.shutdown()
            print('APScheduler finalizado')
            