from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from django.core.management import call_command
from rest_framework.authtoken.models import Token
from django.contrib import messages

from .models import * 
import requests

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [ 'email', 'tab_number', 'name', 'is_chief', 'OGGSK', 'UO', 'MATRIX', 'is_admin', 'job', 'department', 'isChecked']
    search_fields = ['email', 'name']
    list_filter = ['is_chief', 'isChecked', 'OGGSK', 'UO', 'MATRIX', 'is_admin','job', 'department']
    ordering = ['email']
    filter_horizontal = []

    def delete_queryset(self, request, queryset):
        successful_deletions = []
        error_messages = [f"Ошибка при удалении {item}: пользователь присутствует в LDAP" for item in queryset.filter(isChecked=True)]
        
        queryset = queryset.exclude(isChecked=True)

        data = list(queryset.values_list('id', flat=True))

        if data:
            user_token, _ = Token.objects.get_or_create(user=request.user)
            headers = {
                'Authorization': f'{user_token.key}',
                'Content-Type': 'application/json',
            }

            for id in data:
                response = requests.delete(f'http://0.0.0.0:8080/api/v1/delete_data/{id}', headers=headers)

                if response.status_code == 200:
                    successful_deletions.append(id)
                else:
                    error_messages.append(f"Ошибка при удалении {queryset.get(id=id)}: {response.status_code} - {response.text}")
            
            queryset.filter(id__in=successful_deletions).delete()

            if len(successful_deletions) == len(data):
                messages.success(request, "Пользователи успешно удалены.")
            else:
                messages.warning(request, f"Некоторые пользователи были успешно удалены, остальные не были удалены из-за ошибок.")
            for error_message in error_messages:
                messages.error(request, error_message)
        
        return queryset.none()

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

admin.site.unregister(Group)