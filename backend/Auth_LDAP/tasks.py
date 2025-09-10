from backend.celery import app
from django.core.management import call_command

@app.task
def sync_users():
    call_command('sync_ldap_users')

@app.task
def check_notifys():
    call_command('send_notifies')
