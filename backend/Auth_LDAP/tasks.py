from datetime import datetime
from .models import NotifyTask
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import password as ps
from django.db.models import F, ExpressionWrapper, DurationField, Q
from backend.celery import app
from django.core.management import call_command

@app.task
def sync_users():
    out = call_command('sync_ldap_users')
    return out

@app.task
def check_notifys():
    current_date = datetime.now()
    queryset = NotifyTask.objects.all().exclude(last_update=current_date)

    queryset = NotifyTask.objects.annotate(
        difference=ExpressionWrapper(
            F('finish_date') - current_date,
            output_field=DurationField()
        )
    ).filter(
        Q(difference__isnull=False) &
        (Q(difference__days__mod=F('period')) | Q(finish_date=current_date)),
    )
    

    msg_out = 'Сообщений для отправки нет'
    counter = 0
    if queryset.count() > 0:
        try:
            server = smtplib.SMTP(ps.EMAIL_HOST, ps.EMAIL_PORT)
            server.starttls()
            server.login(ps.EMAIL_HOST_USER, ps.LDAP_HOST_USER_PASSWORD)
        except Exception as e:
            return f"Ошибка при подключении к smtp: {e}"
    
        for item in queryset:
            try:
                msg = constructor_msg(item)

                server.sendmail(ps.EMAIL_HOST_USER, item.target.email, msg.as_string())
                counter += 1
            except Exception as e:
                print(f"Ошибка отправки сообщения пользователю: {e}")

        server.quit()
        msg_out = f'Сообщений отправленно - {counter}'

    queryset.update(last_update=current_date)
    
    queryset.filter(finish_date=current_date).delete()

    return msg_out

def constructor_msg(notify: NotifyTask):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'{notify.type_message} | {notify.header}'
    msg['From'] = ps.EMAIL_HOST_USER
    msg['To'] = notify.target.email

    text = 'text'
    html = f"""\
    <html>
            <body>
                <h1 align="center">{notify.title}</h1>
                <p>{notify.message}</p>
            </body>
    </html>
    """

    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    return msg
    