from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


@api_view(['POST'])
def ldap_authorization(request):
    username = request.data.get('username')
    password = request.data.get('password')
    system = request.data.get('system', 'is_superuser')
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({'error': 'Ошибка авторизации'}, status=status.HTTP_401_UNAUTHORIZED)
    if getattr(user, system, False) or user.is_superuser:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    else:
        return Response({'error': 'Доступ пользователю в систему запрещен'}, status=status.HTTP_403_FORBIDDEN)
