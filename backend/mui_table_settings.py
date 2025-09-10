from Auth_LDAP.models import CustomUser
from datetime import datetime, timedelta
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, F, ExpressionWrapper, Subquery, OuterRef, When, Prefetch

# FILTER_OPERATIONS = {
#     'equals': lambda q, f, v: q.filter(**{f: v}),
#     'notEquals': lambda q, f, v: q.exclude(**{f: v}),
#     'contains': lambda q, f, v: q.filter(**{f + '__icontains': v}),
#     'doesNotContain': lambda q, f, v: q.exclude(**{f + '__icontains': v}),
#     'startsWith': lambda q, f, v: q.filter(**{f + '__istartswith': v}),
#     'endsWith': lambda q, f, v: q.filter(**{f + '__iendswith': v}),
#     'greaterThan': lambda q, f, v: q.filter(**{f + '__gt': v}),
#     'greaterThanOrEqual': lambda q, f, v: q.filter(**{f + '__gte': v}),
#     'lessThan': lambda q, f, v: q.filter(**{f + '__lt': v}),
#     'lessThanOrEqual': lambda q, f, v: q.filter(**{f + '__lte': v}),
#     'isEmpty': lambda q, f, v: q.filter(**{f + '__isnull': True}),
#     'isNotEmpty': lambda q, f, v: q.exclude(**{f + '__isnull': True}),
    
#     # Для числовых значений
#     '=': lambda q, f, v: q.filter(**{f: v}),
#     '>': lambda q, f, v: q.filter(**{f + '__gt': v}),
#     '<': lambda q, f, v: q.filter(**{f + '__lt': v}),
#     '>=': lambda q, f, v: q.filter(**{f + '__gte': v}),
#     '<=': lambda q, f, v: q.filter(**{f + '__lte': v}),
    
#     # Для дат
#     'is': lambda q, f, v: q.filter(**{f: v}),
#     'not': lambda q, f, v: q.exclude(**{f: v}),
#     'after': lambda q, f, v: q.filter(**{f + '__gt': v}),
#     'before': lambda q, f, v: q.filter(**{f + '__lt': v}),
#     'onOrAfter': lambda q, f, v: q.filter(**{f + '__gte': v}),
#     'onOrBefore': lambda q, f, v: q.filter(**{f + '__lte': v}),
# }

# def filter_queryset(queryset, filters): 
#     if not queryset.exists():
#         return queryset
#     user_field = 'user' if 'user' in list(queryset.values().first().keys()) else 'id'

#     for filter in filters:
#         field = filter.get('field')
#         value = filter.get('value')
#         operator = filter.get('operator')

#         if field:
#             if field in ['user', 'responsible']:
#                 sub_query = list(FILTER_OPERATIONS[operator](CustomUser.objects, 'name', value).values_list('id', flat=True))
#                 queryset = queryset.filter(**{f'{field}__in':sub_query})
#             elif field in ['department']:
#                 sub_query = list(FILTER_OPERATIONS[operator](CustomUser.objects.using('auth_db'), 'department__name', value).values_list('id', flat=True))
#                 queryset = queryset.filter(**{f'{user_field}__in': sub_query})
#             elif field in ['job']:
#                 sub_query = list(FILTER_OPERATIONS[operator](CustomUser.objects.using('auth_db'), 'job__name', value).values_list('id', flat=True))
#                 queryset = queryset.filter(**{f'{user_field}__in': sub_query})
#             elif field in ['date_start', 'date_control', 'date_nearest']:
#                 date_value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').date()
#                 queryset = FILTER_OPERATIONS[operator](queryset, field, date_value)
#             elif operator in FILTER_OPERATIONS:
#                 queryset = FILTER_OPERATIONS[operator](queryset, field, value)
#     return queryset

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
