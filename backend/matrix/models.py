from django.db import models
from Auth_LDAP.models import *

class Systems(models.Model):
    class Meta:
        verbose_name = 'Система'
        verbose_name_plural = 'Системы'

    name = models.CharField(verbose_name='Наименование', max_length=500)
    parent = models.ForeignKey("self", blank=True, null=True, verbose_name="Родитель", on_delete=models.CASCADE)

    def __str__(self) -> str:
        if self.parent:
            return f"{self.parent} --> {self.name}"
        else:
            return self.name

class Roles(models.Model):
    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        
    name = models.CharField(verbose_name='Наименование', max_length=500)
    
    def __str__(self) -> str:
        return self.name

class UserRoles(models.Model):
    class Meta:
        verbose_name = 'Роли пользователя'
        verbose_name_plural = 'Роли пользователей'

    user = models.ForeignKey(CustomUser, verbose_name="Пользователь", on_delete=models.CASCADE)
    system = models.ForeignKey(Systems, verbose_name='Система', on_delete=models.CASCADE)
    role = models.ForeignKey(Roles, verbose_name='Роль', on_delete=models.CASCADE)
    isChecked = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.user} - {self.role}'

class LogUpdates(models.Model):
    class Meta:
        verbose_name = 'Логи'
        verbose_name_plural = 'Логи'

    system = models.ForeignKey(Systems, verbose_name='Система', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, verbose_name="Пользователь", on_delete=models.CASCADE)
    date_msg = models.DateTimeField(verbose_name='Дата обновления', auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.user} - {self.date_msg}'