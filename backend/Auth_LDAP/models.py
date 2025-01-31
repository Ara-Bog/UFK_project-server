from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class Jobs(models.Model):
    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        
    name = models.CharField(verbose_name='Наименование', max_length=500)
    unique = models.CharField(verbose_name='Ключ к LDAP', max_length=300)
    sortBy = models.IntegerField(default=100, verbose_name='Порядковый номер')
    showName = models.CharField(blank=True, null=True, verbose_name='Отображаемое имя', max_length=300)
    job_inflected = models.CharField(blank=True, null=True, max_length=255, verbose_name="Должность в Д.П.")

    def __str__(self):
        return f'{self.name}' 
    
class Departments(models.Model):
    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'
        
    name = models.CharField(verbose_name='Наименование', max_length=500)
    unique = models.CharField(verbose_name='Ключ к LDAP', max_length=300)
    sortBy = models.IntegerField(default=100, verbose_name='Порядковый номер')
    showName = models.CharField(blank=True, null=True, verbose_name='Отображаемое имя', max_length=300)
    department_inflected = models.CharField(blank=True, null=True, max_length=255, verbose_name="Отдел в Р.П.")

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
        user.is_chief = True
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

    ## Склонение текстовых полей
    name_inflected = models.CharField(blank=True, null=True, max_length=255, verbose_name="ФИО в Д.П.")

    
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_chief = models.BooleanField(default=False)
    OGGSK = models.BooleanField(default=False)
    UO = models.BooleanField(default=False)
    MATRIX = models.BooleanField(default=False)
    
    objects = CustomUserManager()

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
    