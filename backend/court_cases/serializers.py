from rest_framework import serializers
from .models import CourtCases, EventsCourtCases
from datetime import date, timedelta
from Auth_LDAP.models import * 

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ('password', 'last_login', 'ldap_id', 'name_key', 'username')
        depth = 1

class EventsCourtCasesSerializer(serializers.ModelSerializer):
    event__name = serializers.SerializerMethodField()

    class Meta:
        model = EventsCourtCases
        fields = '__all__'

    def get_event__name(self, event):
        return str(event.type_event)
    
class NotifyTasksSerializer(serializers.ModelSerializer):
    court__number_case_in_first_instance = serializers.SerializerMethodField()
    court__number_case_in_numenklature = serializers.SerializerMethodField()
    type_message__name = serializers.SerializerMethodField()

    class Meta:
        model = NotifyTask
        exclude = ('content_type',)
        depth = 1
    
    def get_court__number_case_in_first_instance(self, obj):
        if isinstance(obj.content_object, CourtCases):
            return obj.content_object.number_case_in_first_instance
        return None
    
    def get_court__number_case_in_numenklature(self, obj):
        if isinstance(obj.content_object, CourtCases):
            return obj.content_object.number_case_in_numenklature
        return None
    
    def get_type_message__name(self, obj):
        return obj.type_message.name
    
class CourtCasesNoNotifySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourtCases
        fields = '__all__'
    
class CourtCasesSerializer(serializers.ModelSerializer):
    events = EventsCourtCasesSerializer(many=True, read_only=True)
    date_nearest = serializers.DateField(read_only=True)
    notifyes = serializers.SerializerMethodField()
    max_event_type = serializers.SerializerMethodField()
    is_red = serializers.SerializerMethodField()

    class Meta:
        model = CourtCases
        fields = '__all__'

    def get_notifyes(self, court):
        queryset = court.notify_tasks.filter(target=court.user.id)
        return NotifyTasksSerializer(queryset, many=True).data

    def get_max_event_type(self, court):
        max_event = court.events.order_by('type_event_id').last()
        return max_event.type_event.id if max_event else None
    
    def get_is_red(self, court):
        today = date.today()
        if court.user:
            notify_queryset = court.notify_tasks.filter(target=court.user, system="UO")
            return notify_queryset.filter(date_finish__lte=today + timedelta(days=7)).exists()
        return False
    
class NotifyFromCourtCase(serializers.ModelSerializer):
    notifyes = serializers.SerializerMethodField()

    class Meta:
        model = CourtCases
        fields = ('id', 'number_case_in_first_instance', 'number_case_in_numenklature', 'notify_tasks')

    def get_notifyes(self, court):
        queryset = court.notify_tasks.filter(target=court.user.id)
        return NotifyTasksSerializer(queryset, many=True).data

