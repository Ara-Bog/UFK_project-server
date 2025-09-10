from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

SYSTEMS = {
    "UO": "Юристы",
    "OGGSK": "Кадры",
    "MATRIX": "Матрица",
}

class Jobs(models.Model):
    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        ordering = ['sortBy']
        
    name = models.CharField(verbose_name='Наименование', max_length=500)
    unique = models.CharField(verbose_name='Ключ к LDAP', max_length=300)
    sortBy = models.IntegerField(default=100, verbose_name='Порядковый номер')
    showName = models.CharField(blank=True, null=True, verbose_name='Отображаемое имя', max_length=300)
    DAT_job = models.CharField(blank=True, null=True, max_length=255, verbose_name="Должность в Д.П.")
    RAD_job = models.CharField(blank=True, null=True, max_length=255, verbose_name="Должность в Р.П.")

    def __str__(self):
        return f'{self.name}' 
    
class Departments(models.Model):
    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'
        ordering = ['sortBy']
        
    name = models.CharField(verbose_name='Наименование', max_length=500)
    unique = models.CharField(verbose_name='Ключ к LDAP', max_length=300)
    sortBy = models.IntegerField(default=100, verbose_name='Порядковый номер')
    showName = models.CharField(blank=True, null=True, verbose_name='Отображаемое имя', max_length=300)
    RAD_department = models.CharField(blank=True, null=True, max_length=255, verbose_name="Отдел в Р.П.")

    def __str__(self):
        return f'{self.name}' 
    
class CustomUserManager(BaseUserManager):
    def create_user(self, email: str, job: str, password=None, **extra_fields):
        user = self.model(
            email = self.normalize_email(email),
            job = job,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self.db)

        return user
    
    def create_superuser(self, email: str, name: str, job: str, username: str, password=None, **extra_fields):
       
        user = self.model(
            email = self.normalize_email(email),
            name = name,
            job = job,
            username=username,
            **extra_fields,
        )
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self.db)

        return user

class CustomUser(AbstractBaseUser):    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    ldap_id = models.CharField(max_length=255, verbose_name="ID LDAP")
    tab_number = models.IntegerField(blank=True, null=True, verbose_name='Табельный номер', unique=True)
    email = models.EmailField(unique=True, verbose_name='Почта')
    job = models.ForeignKey(Jobs, blank=True, null=True, on_delete=models.PROTECT, verbose_name="Должность")
    name = models.CharField(max_length=255, verbose_name="ФИО")
    name_key = models.CharField(max_length=255, verbose_name="name_key")
    department = models.ForeignKey(Departments, blank=True, null=True, on_delete=models.PROTECT, verbose_name="Отдел")
    username = models.CharField(max_length=255, unique=True)
    isChecked = models.BooleanField(verbose_name="Прошел проверку в LDAP", default=False, editable=False)
    manually_added = models.BooleanField(verbose_name="Добавлен вручную", default=False)
    isDisabled = models.BooleanField(verbose_name="Блокирован", default=False)
    isFired = models.BooleanField(verbose_name="Уволен", default=False)
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Описание")
    secret = models.BooleanField(default=False, verbose_name="Доступ к секретке")

    ## Склонение текстовых полей
    DAT_name = models.CharField(blank=True, null=True, max_length=255, verbose_name="ФИО в Д.П.")
    RAD_name = models.CharField(blank=True, null=True, max_length=255, verbose_name="ФИО в Р.П.")

    objects = CustomUserManager()
    
    is_superuser = models.BooleanField(default=False)
    manager_rule = models.BooleanField(default=False, verbose_name="Роль руководитель")
    chief_rule = models.BooleanField(default=False, verbose_name="Роль начальник")
    # Доступы к системам
    is_admin = models.BooleanField(default=False, verbose_name="Админ")
    OGGSK = models.BooleanField(default=False, verbose_name="ОГГСиК")
    UO = models.BooleanField(default=False, verbose_name="ЮО")
    MATRIX = models.BooleanField(default=False, verbose_name="Матрица")

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']

    def __str__(self):
        list_name = self.name.split(' ')
        return f'{list_name[0]} {list_name[1][0] if len(list_name) > 1 else ""}.{f"{list_name[2][0]}." if len(list_name) > 2 else ""}'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
        
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser or self.is_admin
    
class TypesNotify(models.Model):
    class Meta:
        verbose_name = 'Тип уведомления'
        verbose_name_plural = 'Типы уведомлений'

    name = models.TextField(verbose_name='Наименование')

    def __str__(self) -> str:
        return self.name

class NotifyTask(models.Model):
    class Meta:
        verbose_name = 'Задача на уведомление'
        verbose_name_plural = 'Задачи на уведомления'

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    system = models.CharField(max_length=10, choices=SYSTEMS, verbose_name='Система')
    type_message = models.ForeignKey(TypesNotify, on_delete=models.PROTECT, verbose_name="Тип уведомления")
    target = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")

    header = models.TextField(verbose_name='Тема сообщения')
    title = models.TextField(verbose_name='Заголовок сообщения')
    message = models.TextField(verbose_name='Текст сообщения')

    period = models.IntegerField(verbose_name='Каждые N дней', default=1)
    date_finish = models.DateField(verbose_name="Крайний срок") 
    date_last_update = models.DateField(verbose_name="Последняя дата проверки") 

    def __str__(self) -> str:
        return f'Для {self.target} | {self.header} | {self.type_message}'

class DocTemplate(models.Model):
    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'system'], name='file_to_system'
            )
        ]

    name = models.CharField(max_length=255, verbose_name="Системное имя файла")
    name_visible = models.CharField(max_length=255, verbose_name="Отображаемое имя файла")
    description = models.TextField(blank=True, verbose_name="Описание")
    system = models.CharField(max_length=10, choices=SYSTEMS, verbose_name='Система')
    file = models.FileField(verbose_name="Файл шаблона") 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Сначала сохраняем объект
        super().save(*args, **kwargs)
        
        # Очищаем старые файлы после сохранения
        self.cleanup_old_files()

    def cleanup_old_files(self):
        """
        Удаляет старые файлы, оставляя только 2 последних для каждой комбинации name+system
        """
        try:
            # Получаем все файлы с таким же name и system, отсортированные по дате создания
            files = DocTemplate.objects.filter(
                name=self.name,
                system=self.system
            ).order_by('-created_at')
            # Удаляем все файлы кроме двух последних
            for file_obj in files[2:]:
                # Безопасно удаляем физический файл
                self.safe_delete_file(file_obj.file)
                # Удаляем запись из базы
                file_obj.delete()
                
        except ObjectDoesNotExist:
            # Если что-то пошло не так, просто продолжаем
            pass

    def safe_delete_file(self, file_field):
        """
        Безопасно удаляет файл с обработкой ошибок
        """
        if file_field:
            try:
                if file_field.storage.exists(file_field.name):
                    file_field.delete(save=False)
            except (ValueError, OSError, FileNotFoundError) as e:
                # Логируем ошибку, но не прерываем выполнение
                print(f"Не удалось удалить файл {file_field.name}: {e}")

    def delete(self, *args, **kwargs):
        """
        Переопределяем удаление, чтобы удалять и физический файл
        """
        self.safe_delete_file(self.file)
        super().delete(*args, **kwargs)