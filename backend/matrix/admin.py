from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import *
from django.db.models import Q
from Auth_LDAP.models import *
# Register your models here.

@admin.register(LogUpdates)
class LogUpdatesAdmin(admin.ModelAdmin):
    list_display = ['user', 'system', 'date_msg']
    search_fields = ['user', 'system__name']
    list_filter = ['date_msg']
    ordering = ['date_msg']


@admin.register(Systems)
class SystemsAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    search_fields = ['name', 'parent']
    ordering = ['name']

@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']

@admin.register(UserRoles)
class UserRolesAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'system']
    search_fields = ['user', 'role__name']
    ordering = ['user', 'role']
