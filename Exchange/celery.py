import os

from celery import Celery
from celery_amqp_backend import AMQPBackend

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Exchange.settings')

app = Celery('Exchange')
# app.conf.result_backend = 'redis://localhost:6379/0'
# app.conf.result_backend = AMQPBackend(app, url='amqp://guest@127.0.0.1:5672')
app.conf.result_backend = 'celery_amqp_backend.AMQPBackend://guest@127.0.0.1:5672'
app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Asia/Tehran',
    enable_utc=True,
)


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')