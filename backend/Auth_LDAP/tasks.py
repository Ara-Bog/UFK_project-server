from datetime import datetime
from .models import NotifyTask
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import password as ps
from django.db.models import F, ExpressionWrapper, DurationField, Q
from backend.celery import app
from django.core.management import call_command
from django.utils import timezone

@app.task
def sync_users():
    call_command('sync_ldap_users')

@app.task
def check_notifys():
    call_command('send_notifies')
