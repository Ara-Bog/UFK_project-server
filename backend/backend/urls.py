"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from Auth_LDAP.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ldap/api/v1/auth', ldap_authorization, name="authorization"),
    path('ldap/api/v1/sync_users', sync_users, name="sync_users"),
    path('ldap/api/v1/generate_doc', generate_docx, name="generate_doc"),
    path('ldap/api/v1/get_file', get_document, name="get_file"),
    path('ldap/api/v1/upload_templates', upload_templates, name="upload_templates"),
    # API vacations
    path('vacations/', include('vacations.urls')),
    # API court_cases
    path('court_cases/', include('court_cases.urls')),
    # API matrix
    path('matrix/', include('matrix.urls'))
]
