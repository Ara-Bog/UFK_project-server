from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.core.management import call_command
from docxtpl import DocxTemplate
from io import BytesIO
from .models import DocTemplate
from django.http import HttpResponse, FileResponse
from urllib.parse import quote
import os
from consts import MIME_TYPES

MONTH_GENITIVE = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря'
}

VARIANTS_DOC = {
    'noPay': 'Без содержания',
    'vacation': 'Отпуск',
    'noPlan': 'Вне графика',
    'vozlozhenie': 'Возложение',
    'vacationNoPay': 'Отпуск без содержания',
    'sickLeave': 'Больничный'
}

def generate_document_content(dataset, type_doc, system, doc_for=''):
    """Генерация содержимого документа"""
    
    def get_string_date(date):
        try:
            [day, month, year] = date.split('.')
            return f'{day}\u202F{MONTH_GENITIVE[int(month)]}\u202F{year}\u202Fг.'
        except Exception as e:
            return "!!ERROR!!"

    dataset['get_string_date'] = get_string_date

    try:
        template = DocTemplate.objects.get(system=system, name=type_doc)
    except DocTemplate.DoesNotExist:
        raise Exception(f'Документ с типом {type_doc} в системе {system} не найден')
    
    # Обрабатываем условия
    doc = DocxTemplate(template.file.path)
    try:
        doc.render(dataset)

        output = BytesIO()
        doc.save(output)
        output.seek(0)

        filename = f"{template.name_visible}-{VARIANTS_DOC.get(dataset['doc_settings']['variant'], '')}{f'-{doc_for}' if doc_for else ''}.docx"
        
        return {
            'content': output.getvalue(),
            'filename': filename,
            'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
    except Exception as e:
        raise Exception(f'Ошибка формирования шаблона: {e}')

@api_view(['POST'])
def ldap_authorization(request):
    username = request.data.get('username')
    password = request.data.get('password')
    system = request.data.get('system', 'is_admin')
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({"message": 'Ошибка авторизации'}, status=status.HTTP_401_UNAUTHORIZED)
    if getattr(user, system, False) or user.is_superuser or user.is_admin:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    else:
        return Response({"message": 'Доступ пользователю в систему запрещен'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def sync_users(request):
    out = call_command('sync_ldap_users')
    return Response(data=out, status=status.HTTP_202_ACCEPTED)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_templates(request):
    """Загрузка шаблонного документа"""

    file = request.FILES['file']
    type_doc = request.data.get('type_doc', 'Unnamed')
    system = request.data.get('system', '')
    
    if not system:
        return Response("Не указано наименование системы", status=status.HTTP_400_BAD_REQUEST)

    template, _ = DocTemplate.objects.update_or_create(
        system=system,
        name=type_doc,
        file=file
    )
    
    return Response({"message": "Файл успешно загружен в систему", "template_id": template.id}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_document(request):
    system = request.GET.get('system', None)
    type_doc = request.GET.get('type_doc', None)

    try:
        template = DocTemplate.objects.get(system=system, name=type_doc)

        # Открываем файл в бинарном режиме
        file = open(template.file.path, 'rb')
        
        # Создаем FileResponse с правильными заголовками
        response = FileResponse(file)

        original_filename = template.file.name
        _, file_extension = os.path.splitext(original_filename)
        download_filename = f"{template.name_visible}{file_extension}"
        quoted_filename = quote(download_filename)
        # Устанавливаем заголовки для скачивания
        response['Content-Disposition'] = f'attachment; filename="{quoted_filename}"'
        
        response['Content-Type'] = MIME_TYPES.get(file_extension.lower(), 'application/octet-stream')
        
        return response
    except DocTemplate.DoesNotExist as e:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def generate_docx(request):
    """Генерация выходного doc по шаблону"""
    dataset = request.data.get('dataset', {})
    type_doc = request.data.get('type_doc', 'None')
    system = request.data.get('system', 'None')
    doc_for = request.data.get('doc_for', '')
    
    try:
        result = generate_document_content(dataset, type_doc, system, doc_for)
        
        response = HttpResponse(
            result['content'],
            content_type=result['content_type']
        )
        response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{quote(result["filename"])}'
        return response
        
    except Exception as e:
        return Response(
            str(e), 
            status=status.HTTP_400_BAD_REQUEST
        )
