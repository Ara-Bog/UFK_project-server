from Auth_LDAP.models import CustomUser
from datetime import datetime
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q


def filter_queryset(queryset, filters):
    if not queryset.exists():
        return queryset
    
    q_objects = Q()

    is_user = queryset.model == CustomUser
    
    for filter_item in filters:
        field = filter_item.get('field')
        value = filter_item.get('value')
        operator = filter_item.get('operator')

        if not field or value is None:
            continue
        
        if field in ['user', 'responsible']:
            # Фильтруем по имени пользователя через связанную модель
            condition = create_q_condition(f'{field}__name', operator, value)
        elif field in ['department', 'job']:
            # Фильтруем по названию отдела
            condition = create_q_condition(f'{"" if is_user else "user__"}{field}__name', operator, value)
        elif field.startswith('date_'):
            # Преобразуем строку в дату
            try:
                date_value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').date()
                condition = create_q_condition(field, operator, date_value)
            except (ValueError, TypeError):
                condition = None
        else:
            condition = create_q_condition(field, operator, value)
            
        if condition:
            q_objects &= condition
    
    return queryset.filter(q_objects)

def get_ordering_field(model, field_name):
    is_user = model == CustomUser 
    if field_name in ['user', 'responsible']:
        return f'{field_name}__name'
    elif field_name in ['department', 'job']:
        prefix = '' if is_user else 'user__'
        return f'{prefix}{field_name}__name'
    else:
        return field_name

def create_q_condition(field, operator, value):
    """
    Создает Q-объект для условия фильтрации
    """
    conditions = {
        'equals': Q(**{field: value}),
        'notEquals': ~Q(**{field: value}),
        'contains': Q(**{f'{field}__icontains': value}),
        'doesNotContain': ~Q(**{f'{field}__icontains': value}),
        'startsWith': Q(**{f'{field}__istartswith': value}),
        'endsWith': Q(**{f'{field}__iendswith': value}),
        'greaterThan': Q(**{f'{field}__gt': value}),
        'greaterThanOrEqual': Q(**{f'{field}__gte': value}),
        'lessThan': Q(**{f'{field}__lt': value}),
        'lessThanOrEqual': Q(**{f'{field}__lte': value}),
        'isEmpty': Q(**{f'{field}__isnull': True}),
        'isNotEmpty': ~Q(**{f'{field}__isnull': True}),
        
        # Числовые операции
        '=': Q(**{field: value}),
        '>': Q(**{f'{field}__gt': value}),
        '<': Q(**{f'{field}__lt': value}),
        '>=': Q(**{f'{field}__gte': value}),
        '<=': Q(**{f'{field}__lte': value}),
        
        # Операции для дат
        'is': Q(**{field: value}),
        'not': ~Q(**{field: value}),
        'after': Q(**{f'{field}__gt': value}),
        'before': Q(**{f'{field}__lt': value}),
        'onOrAfter': Q(**{f'{field}__gte': value}),
        'onOrBefore': Q(**{f'{field}__lte': value}),
    }
    
    return conditions.get(operator)

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'pageSize'
    page_size = 10  # Значение по умолчанию
