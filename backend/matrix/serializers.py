from rest_framework import serializers
from .models import *
from Auth_LDAP.models import *

class UserSerializer(serializers.ModelSerializer):
    last_update = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'department', 'job', 'name', 'last_update', 'description', 'isDisabled', 'isFired']
        depth=1

    def get_last_update(self, obj):
        try:
            last_date = LogUpdates.objects.filter(user=obj.id).order_by('-date_msg').first()
            return last_date.date_msg.strftime('%d.%m.%Y %H:%M:%S')
        except Exception:
            return None

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'

class SystemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Systems
        fields = '__all__'


