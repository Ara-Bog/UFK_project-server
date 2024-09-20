from django.contrib.auth import get_user_model
from django_auth_ldap.backend import LDAPBackend

UserModel = get_user_model()

class CustomModelBackend(LDAPBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)

        if user is not None:
            user_model = UserModel._default_manager.get(username=user.username)

        return user