from __future__ import absolute_import
import os
from celery import Celery
from celery.signals import setup_logging  # noqa
from django.conf import settings



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
	CELERY_ACCEPT_CONTENT = ['json'],
	CELERY_TASK_SERIALIZER = 'json',
    BROKER_URL           = 'amqp://crawler:crawlerpazz@localhost:5672/craw',
	CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler',
    CELERY_TASK_DEFAULT_QUEUE = "craw_queu",
    CELERY_CREATE_MISSING_QUEUES = True,
    CELERY_DEFAULT_EXCHANGE = "craw_exchange",
    CELERY_TIMEZONE = "America/Santiago",
    # CELERY_DEFAULT_ROUTING_KEY = "mybinance",
    CELERY_RESULT_BACKEND = "django-db",
    )


app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))