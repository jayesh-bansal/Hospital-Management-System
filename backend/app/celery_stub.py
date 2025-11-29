from celery import Celery
from celery.schedules import crontab
from .config import Config
celery_app = Celery('hms', broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)
celery_app.conf.update(
    result_expires=3600,
    task_always_eager=True,
    task_eager_propagates=True,
    beat_schedule={
        'daily-reminder-8am': {
            'task': 'app.tasks.daily_reminder_task',
            'schedule': crontab(hour=8, minute=0),
        },
    }
)
