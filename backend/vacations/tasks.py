from backend.celery import app
from django.core.management import call_command

@app.task
def delete_old():
    call_command('remove_old_vacations')
