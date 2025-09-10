from django.db import models
from django.db import models
from Auth_LDAP.models import CustomUser

class PeriodsVacation(models.Model):
    class Meta:
        verbose_name = 'Период отпуска'
        verbose_name_plural = 'Периоды отпуска'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Сотрудник')
    period_start = models.DateField(verbose_name='Дата начала периода работы')
    period_end = models.DateField(verbose_name='Дата окончания периода работы')
    
    def __str__(self):
        return f"с {self.period_start.strftime('%d.%m.%Y')} по {self.period_end.strftime('%d.%m.%Y')}"

class Vacations(models.Model):
    class Meta:
        verbose_name = 'Отпуск'
        verbose_name_plural = 'Отпуска'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Сотрудник', related_name='uservacations_as_user')
    date_start = models.DateField(verbose_name='Дата начала отпуска')
    count_days = models.IntegerField(verbose_name='Количество дней отпуска')
    responsible = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Ответственный', related_name='uservacations_as_responsible')
    edv = models.BooleanField(verbose_name='Единовременная выплата', default=False)
    mat = models.BooleanField(verbose_name='Мат. помощь', default=False)
    user_created = models.CharField(verbose_name='Кем создан', max_length=255)

    is_archive = models.BooleanField(verbose_name='Архивный', default=False)
    is_transfered = models.BooleanField(verbose_name='Перенесен', default=False)
    is_merged = models.BooleanField(verbose_name='Объеденен', default=False)
    create_by_transfered = models.BooleanField(verbose_name='Создан переносом', default=False)
    
    # для формирования файлов
    date_end = models.DateField(null=True, blank=True, verbose_name='Дата окончания отпуска')
    order_number = models.CharField(null=True, blank=True, verbose_name='Номер приказа', max_length=255)
    order_date = models.DateField(null=True, blank=True, verbose_name='Дата приказа')
    periods = models.ManyToManyField(PeriodsVacation, blank=True, related_name="periods_list")
    
    def __str__(self):
        return f"{self.user} - {self.date_start} на {self.count_days} дней"

class TransactionTransferVacations(models.Model):
    class Meta:
        verbose_name = 'Транзакция переноса отпуска'
        verbose_name_plural = 'Транзакции переноса отпуска'

    user_create = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Сотрудник')
    vacations_drop = models.ManyToManyField(Vacations, related_name="drop_vacations")
    vacations_create = models.ManyToManyField(Vacations, related_name="add_vacations")
    data_create = models.DateField(auto_now_add=True, verbose_name='Дата изменения')
    time_create = models.TimeField(auto_now_add=True, verbose_name='Время изменения')

    def __str__(self):
        return f"{self.data_create} {self.time_create} - {self.user_create}"


class UserSettings(models.Model):
    class Meta:
        verbose_name = 'Настройка пользователя'
        verbose_name_plural = 'Настройки пользователя'
        
    user = models.OneToOneField(CustomUser, primary_key=True, on_delete=models.CASCADE)
    manager = models.ForeignKey(CustomUser,  on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Руководитель', related_name='usersettings_as_manager')
    chief = models.ForeignKey(CustomUser,  on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Начальник отдела', related_name='usersettings_as_chief')
    period = models.IntegerField(verbose_name='Отчетный год')

class Logs(models.Model):
    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    vacation = models.ForeignKey(Vacations, on_delete=models.CASCADE, verbose_name='Отпуск')
    curator = models.CharField(verbose_name='Кто изменил', max_length=255)
    data_create = models.DateField(auto_now_add=True, verbose_name='Дата изменения')
    time_create = models.TimeField(auto_now_add=True, verbose_name='Время изменения')
    changed_filed = models.CharField(blank=True, null=True, verbose_name='Измененное поле', max_length=255)
    changed_value = models.CharField(blank=True, null=True, verbose_name='Измененно с', max_length=255)
    new_value = models.CharField(blank=True, null=True, verbose_name='Измененно на', max_length=255)
