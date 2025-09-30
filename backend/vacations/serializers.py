from rest_framework import serializers
from .models import *
from Auth_LDAP.models import *
import backend.settings as settings
from datetime import timedelta
import datetime

VACATION_DICTONARY = {
    'responsible': "Ответственный",
    'order_number': "Номер приказа",
    'tab_number': "Табельный номер",
    'edv': "ЕДВ",
    'mat': "Мат. помощь",
    'create': 'create',
    'load': 'load',
    'date_start': 'Дата начала',
    'date_end': 'Дата окончания',
    'order_date': 'Дата приказа',
    'number_order': 'Номер приказа',
    'periods': 'Периоды',
    'is_cancel': "Статус отмены",
    'is_transfered': "is_transfered",
    'is_merged': "is_merged",
    'create_by_transfered': "create_by_transfered",
    'is_archive': "Статус архива",
    'count_days': 'Количество дней',
}

def format_value(value):
    if type(value) == bool:
        return "Да" if value else "Нет"
    if type(value) == datetime.date:
        return value.strftime("%d.%m.%Y")
    
    return value


def create_log(user, vacation, field, old_value=None, value=""):
    value = format_value(value)
    old_value = format_value(old_value)
    Logs.objects.create(
        curator=str(user),
        vacation_id=vacation.id,
        changed_filed=VACATION_DICTONARY[field],
        changed_value=getattr(vacation, field, "") if old_value == None else old_value,
        new_value=value,
    )

class CustomUserSerializer(serializers.ModelSerializer):
    date_nearest = serializers.SerializerMethodField()
    edv_control = serializers.SerializerMethodField()
    mat_control = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        exclude = ('password', 'last_login', 'ldap_id', 'name_key', 'username')
        extra_fields = [
            'date_nearest', 'edv_control', 'mat_control'
        ]
        depth = 1

    def get_date_nearest(self, obj):
        vacation = Vacations.objects.filter(user=obj.id, is_archive=False, is_transfered=False).order_by('date_start').first()
        return vacation.date_start.strftime('%d.%m.%Y') if vacation else None

    def get_edv_control(self, obj):
        return Vacations.objects.filter(user=obj.id, edv=True).exists()
    
    def get_mat_control(self, obj):
        return Vacations.objects.filter(user=obj.id, mat=True).exists()

class PeriodsSerializer(serializers.ModelSerializer):
    period_start = serializers.DateField(
        input_formats=['%d.%m.%Y', 'iso-8601'], format='%d.%m.%Y')
    period_end = serializers.DateField(
        input_formats=['%d.%m.%Y', 'iso-8601'], format='%d.%m.%Y')

    class Meta:
        model = PeriodsVacation
        fields = '__all__'
        

class BaseVacationSerializer(serializers.ModelSerializer):
    responsible_id = serializers.PrimaryKeyRelatedField(
        source='responsible',  # указываем, что это источник для поля responsible
        queryset=CustomUser.objects.all(),
        required=False,
        allow_null=True,
        write_only=True  # только для записи
    )
    date_start = serializers.DateField(
        input_formats=['%d.%m.%Y', 'iso-8601'], format='%d.%m.%Y')
    date_end = serializers.DateField(
        input_formats=['%d.%m.%Y', 'iso-8601'], format='%d.%m.%Y')
    order_date = serializers.DateField(
        input_formats=['%d.%m.%Y', 'iso-8601'], format='%d.%m.%Y', required=False,
        allow_null=True)
    periods = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=PeriodsVacation.objects.all(), 
        required=False
    )

    class Meta:
        model = Vacations
        fields = '__all__'
        extra_fields = ['date_control']
        depth = 2

    def update(self, instance, validated_data):
        # Получаем текущего пользователя из контекста
        user = self.context['request'].user

        # Создаем словарь измененных полей
        changed_fields = {}
        
        # Сравниваем старые и новые значения
        for field, new_value in validated_data.items():
            old_value = getattr(instance, field)
            
            # Для ForeignKey сравниваем по id
            if isinstance(new_value, models.Model):
                if old_value.id != new_value.id:
                    changed_fields[field] = (old_value, new_value)
            # Для ManyToMany обрабатываем отдельно
            elif field == 'periods':
                old_ids = set(instance.periods.values_list('id', flat=True))
                new_ids = set([p.id for p in new_value])
                if old_ids != new_ids:
                    changed_fields[field] = (list(old_ids), list(new_ids))
            # Для обычных полей
            elif old_value != new_value:
                changed_fields[field] = (old_value, new_value)
        # Вызываем родительский метод для сохранения изменений
        instance = super().update(instance, validated_data)
        
        # Создаем логи для измененных полей
        for field, (old_value, new_value) in changed_fields.items():
            create_log(
                user=user,
                vacation=instance,
                field=field,
                value=new_value,
            )
        
        return instance

    def create(self, validated_data):
        user = self.context['request'].user
        create_by = self.context['create_by']
        
        instance = super().create(validated_data)
        
        create_log(
            user=user,
            vacation=instance,
            field=create_by,
            old_value=False,
            value=True
        )
        
        return instance

    
class VacationSerializer(BaseVacationSerializer):
    edv_control = serializers.SerializerMethodField()
    mat_control = serializers.SerializerMethodField()
    user__name__short = serializers.SerializerMethodField()
    transaction_id = serializers.SerializerMethodField()

    class Meta(BaseVacationSerializer.Meta):
        extra_fields = BaseVacationSerializer.Meta.extra_fields + ['edv_control', 'mat_control', 'user__name__short']

    def get_edv_control(self, obj):
        return Vacations.objects.filter(user=obj.user, edv=True).exclude(id=obj.id).exists()
    
    def get_mat_control(self, obj):
        return Vacations.objects.filter(user=obj.user, mat=True).exclude(id=obj.id).exists()

    def get_user__name__short(self, obj):
        return str(obj.user)
        
    def get_transaction_id(self, obj):
        """Возвращает ID последней транзакции для этого отпуска"""
        # Сначала проверяем, есть ли транзакции, где отпуск был исходным (drop_vacations)
        if obj.drop_vacations.exists():
            return obj.drop_vacations.first().id
        # Если нет — возвращаем транзакцию, где отпуск стал новым (add_vacations)
        elif obj.add_vacations.exists():
            return obj.add_vacations.first().id
        return None  # Если транзакций нет вообще

class VacationListSerializer(BaseVacationSerializer):
    class Meta(BaseVacationSerializer.Meta):
        pass

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['department'] = CustomUserSerializer(instance.user).data['department']
        
        return representation

class TransfersSerializer(serializers.ModelSerializer):
    vacations_drop = VacationSerializer(many=True)
    vacations_create = VacationSerializer(many=True)
    time_create = serializers.TimeField(
        format='%H:%M',
        input_formats=['%H:%M', 'iso-8601'],
    )
    data_create = serializers.DateField(
        input_formats=['%d.%m.%Y', 'iso-8601'], format='%d.%m.%Y')

    class Meta:
        model = TransactionTransferVacations
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_create'] = CustomUserSerializer(instance.user_create).data
        
        return representation
    
class LogsSerializer(serializers.ModelSerializer):
    curator__name = serializers.CharField(source='curator', read_only=True)
    data_create = serializers.DateField(
        input_formats=['%d.%m.%Y', 'iso-8601'], format='%d.%m.%Y')
    time_create = serializers.TimeField(
        input_formats=['%H:%M:%S', '%H:%M', 'iso-8601'], 
        format='%H:%M'  
    )

    class Meta:
        model = Logs
        fields = '__all__'
        extra_fields = ['curator__name']

class UserSettingsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        exclude = ('user',)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        manager_data = CustomUserSerializer(instance.manager).data if instance.manager else None
        chief_data = CustomUserSerializer(instance.chief).data if instance.chief else None
        
        if manager_data:
            manager_data['is_main'] = manager_data.get('job', {}).get('name') == 'Руководитель'
        if chief_data:
            chief_data['is_main'] = chief_data.get('job', {}).get('name') == 'Начальник отдела'

        representation['manager'] = manager_data
        representation['chief'] = chief_data
        
        return representation
    
class UserSettingsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        exclude = ('user',)
 
