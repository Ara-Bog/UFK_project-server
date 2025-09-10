from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import *
from django.db.models import Q, Prefetch, Subquery, OuterRef
from .serializers import *
from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from openpyxl import load_workbook
import os
from django.conf import settings
import io
import datetime

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def search(request):
    query = request.data.get('query')
    if not query:
        return Response("Нет запроса", status=400)

    user_vector = SearchVector('name', 'job__name')
    users = CustomUser.objects.select_related('job').annotate(
        rank=SearchRank(user_vector, SearchQuery(query))
    ).filter(
        Q(name__icontains=query) | Q(email__icontains=query) | Q(job__name__icontains=query)
    )

    dep_vector = SearchVector('name')
    deps = Departments.objects.annotate(
        rank=SearchRank(dep_vector, SearchQuery(query))
    ).filter(
        Q(name__icontains=query)
    )

    results = list(users) + list(deps)
    results.sort(key=lambda x: getattr(x, 'rank', 0), reverse=True)
    results = [
        {
            'id': x.id,
            'name': x.name,
            'email': getattr(x, 'email', None),
            'job__str': x.job.name if hasattr(x, 'job') else None,
            'type': 'user' if isinstance(x, CustomUser) else 'department',
            **({
                'isFired': x.isFired,
                'isDisabled': x.isDisabled
            } if isinstance(x, CustomUser) else {})
        }
        for x in results
    ]

    return Response(results, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def departmentInfo(request, pk):
    users_data = CustomUser.objects.filter(department__id=pk)
    department_name = Departments.objects.get(id=pk).name
    return Response(data={'users': UserSerializer(users_data, many=True).data, 'name': department_name}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def userInfo(request, pk):
    user_data = CustomUser.objects.select_related('job', 'department').get(id=pk)
    
    # Получаем все необходимые данные с аннотациями
    systems_with_data = Systems.objects.filter(
        userroles__user=pk
    ).prefetch_related(
        Prefetch(
            'userroles_set',
            queryset=UserRoles.objects.filter(user=pk).select_related('role'),
            to_attr='user_roles'
        )
    ).annotate(
        last_update=Subquery(
            LogUpdates.objects.filter(
                system=OuterRef('id'), 
                user=pk
            ).order_by('-date_msg').values('date_msg')[:1]
        )
    ).distinct()
    
    # Группируем системы
    parent_systems = systems_with_data.filter(parent__isnull=True)
    child_systems = systems_with_data.filter(parent__isnull=False)
    
    # Формируем ответ
    out_data = []
    for parent in parent_systems:
        parent_data = {
            'id': parent.id,
            'name': parent.name,
            'parent': parent.parent_id,
            'roles': RolesSerializer([ur.role for ur in parent.user_roles], many=True).data,
            'last_update': parent.last_update,
            'subsystems': []
        }
        
        # Добавляем дочерние системы
        for child in child_systems.filter(parent=parent):
            child_data = {
                'id': child.id,
                'name': child.name,
                'parent': child.parent_id,
                'roles': RolesSerializer([ur.role for ur in child.user_roles], many=True).data,
                'last_update': child.last_update
            }
            parent_data['subsystems'].append(child_data)
            
            # Обновляем last_update родителя
            if child.last_update and (
                not parent_data['last_update'] or 
                child.last_update > parent_data['last_update']
            ):
                parent_data['last_update'] = child.last_update
        
        out_data.append(parent_data)
    
    return Response(data={
        'roles': out_data,
        'user': UserSerializer(user_data).data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def rolesUserToExcel(request, pk):
    try:
        template = DocTemplate.objects.get(system='MATRIX', name='roles_user')
        with open(template.file.path, 'rb') as file:
            excel_data = io.BytesIO(file.read())

        wb = load_workbook(excel_data, read_only=False)
        ws = wb["Данные"]

        user_data = CustomUser.objects.get(id=pk)
        roles_queryset = UserRoles.objects.filter(user=pk).order_by('system')

        ws['B3'] = user_data.department.name
        ws['B4'] = user_data.name
        ws['B5'] = user_data.job.name
        ws['B6'] = datetime.datetime.now().strftime("%d.%m.%Y")

        cur_system = None
        cur_subsystem = None
        for i, user_role in enumerate(roles_queryset):
            cur_row = 9 + i

            select_system = user_role.system.parent.name if user_role.role.system.parent else user_role.role.system.name
            select_subsystem = user_role.role.system.name if user_role.role.system.parent else None

            if cur_system != select_system:
                ws[f'A{cur_row}'] = select_system
                ws[f'B{cur_row}'] = select_subsystem
                cur_system = select_system
            elif cur_subsystem != select_subsystem:
                ws[f'B{cur_row}'] = select_subsystem
                cur_subsystem = select_subsystem

            ws[f'E{cur_row}'] = user_role.role.name
            
            if i:
                ws.merge_cells.ranges.add(f'B{cur_row}:D{cur_row}')
                ws.merge_cells.ranges.add(f'E{cur_row}:H{cur_row}')
            ws[f'A{cur_row}']._style = ws['A9']._style
            ws[f'B{cur_row}']._style = ws['A9']._style
            ws[f'C{cur_row}']._style = ws['A9']._style
            ws[f'D{cur_row}']._style = ws['A9']._style
            ws[f'E{cur_row}']._style = ws['A9']._style
            ws[f'F{cur_row}']._style = ws['A9']._style
            ws[f'G{cur_row}']._style = ws['A9']._style
            ws[f'H{cur_row}']._style = ws['A9']._style

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.ms-excel.sheet.macroEnabled.12')
        response['Content-Disposition'] = 'attachment; filename="Данные по сотруднику.xlsx"'
        return response

    except Exception as e:
        print(f"Error processing template file: {e}")
        return Response("Ошибка в формировании файла", status=status.HTTP_409_CONFLICT)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def rolesDepartmentToExcel(request, pk):
    try:
        template = DocTemplate.objects.get(system='MATRIX', name='roles_department')
        with open(template.file.path, 'rb') as file:
            excel_data = io.BytesIO(file.read())

        wb = load_workbook(excel_data, read_only=False)
        ws = wb["Данные"]
        table = ws.tables['Main']

        users_queryset = CustomUser .objects.filter(department=pk)
        roles_queryset = UserRoles.objects.filter(user__in=list(users_queryset.values_list('id', flat=True)))

        ws['A1'] = Departments.objects.get(id=pk).name

        for user_role in roles_queryset:
            parent = user_role.role.system.parent
            main_system = parent.name if parent else user_role.role.system.name

            ws.append([
                users_queryset.get(id=user_role.user).name,
                main_system,
                user_role.role.name if parent else None,
                user_role.role.name,
            ])
        ws.delete_rows(3)
        table.ref = "A2:D" + str(ws.max_row)
            
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.ms-excel.sheet.macroEnabled.12')
        response['Content-Disposition'] = 'attachment; filename="Данные по отделу.xlsx"'
        return response

    except Exception as e:
        print(f"Error processing template file: {e}")
        return Response("Ошибка в формировании файла", status=status.HTTP_409_CONFLICT)