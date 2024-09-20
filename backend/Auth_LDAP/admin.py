from django.contrib import admin
from django.contrib.auth.models import Group

from .models import * 
# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['tab_number', 'email', 'name', 'is_chief', 'OGGSK', 'UO', 'MATRIX', 'is_superuser', 'job', 'department']
    search_fields = ['email', 'name']
    list_filter = ['is_chief', 'OGGSK', 'UO', 'MATRIX', 'is_superuser','job', 'department']
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

admin.site.unregister(Group)