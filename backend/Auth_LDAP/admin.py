from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from django.contrib import messages

from .models import * 
import requests

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [ 'email', 'tab_number', 'name', 'chief_rule', 'manager_rule', 'OGGSK', 'UO', 'MATRIX', 'is_admin', 'job', 'department', 'isChecked', 'manually_added', 'isDisabled', 'isFired']
    search_fields = ['email', 'name']
    list_filter = ['chief_rule', 'manager_rule', 'isChecked', 'isDisabled', 'isFired', 'manually_added', 'OGGSK', 'UO', 'MATRIX', 'is_admin','job', 'department']
    ordering = ['email']
    filter_horizontal = []

@admin.register(Jobs)
class JobsAdmin(admin.ModelAdmin):
    list_display = ['name', 'unique', 'sortBy']
    search_fields = ['name']
    ordering = ['-sortBy']


@admin.register(Departments)
class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ['name', 'unique', 'sortBy']
    search_fields = ['name']
    ordering = ['-sortBy']


@admin.register(TypesNotify)
class TypesNotifyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(NotifyTask)
class NotifyTaskAdmin(admin.ModelAdmin):
    list_display = ['type_message', 'target', 'period', 'date_last_update', 'date_finish']
    list_filter = ['type_message', 'date_last_update', 'date_finish']
    search_fields = ['target']

@admin.register(DocTemplate)
class DocTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'system', 'created_at', 'updated_at']
    list_filter = ['system', 'updated_at']
    search_fields = ['name']

admin.site.unregister(Group)