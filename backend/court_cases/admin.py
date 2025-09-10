from django.contrib import admin
from .models import * 
from Auth_LDAP.models import *
from django.db.models import Q

class EventsInline(admin.TabularInline):
    model = EventsCourtCases
    readonly_fields = ['type_event']
    fields = ['type_event']
    show_change_link = True
    extra = 0

@admin.register(CourtCases)
class CourtsAdmin(admin.ModelAdmin):
    list_display = ['get_court_case', 'category', 'archive', 'is_checked', 'is_loaded']
    list_filter = ['archive', 'is_checked', 'is_loaded']
    inlines = [EventsInline]
    search_fields = ['number_case_in_first_instance', 'number_case_in_numenklature', 'plaintiff', 'category']

    def get_court_case(self, obj):
        return str(obj)

    get_court_case.short_description = 'Дело'

@admin.register(EventsCourtCases)
class EventsAdmin(admin.ModelAdmin):
    list_display = ['court_case', 'type_event']
    search_fields = ['court_case__number_case_in_first_instance', 'court_case__number_case_in_numenklature']
    list_filter = ['type_event']


admin.site.register(TypesEventsCourtCases)