import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend', broker='redis://0.0.0.0:6379')
app.conf.broker_connection_retry = True
app.conf.broker_connection_retry_on_startup = True
app.conf.timezone = 'Europe/Moscow'

app.conf.beat_schedule = {
    'check-tasks-every-day': {
        'task': 'Auth_LDAP.tasks.sync_users',
        'schedule':  crontab(hour=8, minute=0),
    },
    'notify-tasks': {
        'task': 'Auth_LDAP.tasks.check_notifys',
        'schedule':  crontab(hour=9, minute=0),
    },
}

app.autodiscover_tasks()