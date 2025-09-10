from django.core.management.base import BaseCommand
from Auth_LDAP.models import NotifyTask
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import password as ps
from django.utils import timezone

class Command(BaseCommand):
    help = 'Отправка уведомлений'

    def __constructor_msg(notify: NotifyTask):
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
        
    def handle(self, *args, **kwargs):
        current_date = timezone.now().date()
        queryset = NotifyTask.objects.all().exclude(date_last_update=current_date)

        expired_count = NotifyTask.objects.filter(date_finish__lt=current_date).delete()[0]
        self.stdout.write(self.style.SUCCESS(f'{msg_out}. Удалено просроченных: {expired_count}'))
        
        result = []
        for task in queryset:
            delta = (task.date_finish - current_date).days
            if task.period != 0 and delta % task.period == 0:
                result.append(task)
        
        queryset = NotifyTask.objects.filter(id__in=[task.id for task in result])
        
        msg_out = 'Сообщений для отправки нет'
        counter = 0
        if queryset.count() > 0:
            try:
                server = smtplib.SMTP(ps.EMAIL_HOST, ps.EMAIL_PORT)
                server.starttls()
                server.login(ps.EMAIL_HOST_USER, ps.LDAP_HOST_USER_PASSWORD)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Ошибка при подключении к smtp: {e}"))
                return
        
            for item in queryset:
                try:
                    msg = self.__constructor_msg(item)

                    server.sendmail(ps.EMAIL_HOST_USER, item.target.email, msg.as_string())
                    counter += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Ошибка отправки сообщения пользователю: {e}"))

            server.quit()
            msg_out = f'Сообщений отправлено - {counter}'

        queryset.update(date_last_update=current_date)
        
        self.stdout.write(self.style.SUCCESS(msg_out))