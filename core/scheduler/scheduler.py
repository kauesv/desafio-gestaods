from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils.timezone import get_current_timezone

from gamifications.cron import prize_expiration


def start():

    scheduler = BackgroundScheduler(
        timezone=get_current_timezone()
    )

    # ------------------
    # GAMIFICATIONS
    scheduler.add_job(
        prize_expiration,
        trigger=CronTrigger(minute='*/1'),
        id='verifica_premios',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.start()

    return scheduler