from django.contrib import admin
from django.contrib.auth.models import Group, User

from .models import * 
from django.db.models import Q


# @admin.register(CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
#     def get_queryset(self, request):
#         query = super().get_queryset(request)
#         return query.filter(Q(OGGSK=True) | Q(is_admin=True))

#     list_display = ['email', 'name', 'chief_rule', 'is_admin', 'job', 'department']
#     search_fields = ['email', 'name']
#     list_filter = ['chief_rule', 'is_admin','job', 'department']
#     ordering = ['email']
#     filter_horizontal = []


@admin.register(Logs)
class LogsAdmin(admin.ModelAdmin):
    list_display = ['vacation_id', 'curator', 'changed_filed', 'changed_value', 'new_value', 'data_create', 'time_create']
    search_fields = ['data_create', 'curator']
    list_filter = ['data_create', 'curator']
    ordering = ['-data_create', '-time_create']

    # def get_search_results(self, request, queryset, search_term):
    #     queryset, use_distinct = super().get_search_results(request, queryset, search_term)
    #     user_ids = list(CustomUser.objects.filter(name__icontains=search_term).values_list('id', flat=True))

    #     # Добавляем поиск по строковому представлению vacation_id
    #     queryset |= self.model.objects.filter(vacation_id__user__in=user_ids)

    #     return queryset, use_distinct

@admin.register(Vacations)
class VacationsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_start', 'count_days', 'responsible', 'order_number', 'is_transfered', 'is_archive']
    search_fields = ['user', 'responsible', 'order_number']
    list_filter = ['is_transfered', 'is_archive']

    # def get_user(self, obj):
    #     user = CustomUser.objects.get(id=obj.user)
    #     return str(user)

    # def get_responsible(self, obj):
    #     user = CustomUser.objects.get(id=obj.responsible)
    #     return str(user)

    # get_user.short_description = 'Сотрудник'
    # get_responsible.short_description = 'Ответственный'

    # def get_search_results(self, request, queryset, search_term):
    #     queryset, use_distinct = super().get_search_results(request, queryset, search_term)

    #     # Поиск по имени сотрудника
    #     user_ids = list(CustomUser.objects.filter(name__icontains=search_term).values_list('id', flat=True))

    #     # Добавляем фильтрацию по user и responsible
    #     queryset |= self.model.objects.filter(user__in=user_ids) | self.model.objects.filter(responsible__in=user_ids)

    #     return queryset, use_distinct

@admin.register(PeriodsVacation)
class PeriodsVacationAdmin(admin.ModelAdmin):
    list_display = ['user', 'period_start', 'period_end']
    search_fields = ['user']

    # def get_user(self, obj):
    #     user = CustomUser.objects.get(id=obj.user)
    #     return str(user)

    # get_user.short_description = 'Сотрудник'

    # def get_search_results(self, request, queryset, search_term):
    #     queryset, use_distinct = super().get_search_results(request, queryset, search_term)
    #     # Добавляем поиск по имени пользователя
    #     queryset |= self.model.objects.filter(user__in=list(CustomUser.objects.filter(name__icontains=search_term).values_list('id', flat=True)))
    #     return queryset, use_distinct

admin.site.register(TransactionTransferVacations)
admin.site.register(UserSettings)
# admin.site.unregister(Group)
# admin.site.unregister(User)
# admin.site.unregister(Token)