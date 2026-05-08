from django.test import TestCase

class PrizeExpirationTestCase(TestCase):
    def test_scheduler_is_running(self):
        """
        Testa se o scheduler do APScheduler está ativo após ser iniciado.
        """
        from core.scheduler.scheduler import start

        scheduler = start()
        self.assertTrue(scheduler.running)
        # Não esqueça de desligar o scheduler para não interferir em outros testes
        scheduler.shutdown()