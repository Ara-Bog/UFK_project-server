from django.urls import path
from matrix.views import *

urlpatterns = [
    path('api/v1/user/<int:pk>', userInfo, name='user_info'),
    path('api/v1/department/<int:pk>', departmentInfo, name='department_users'),
    path('api/v1/search/', search, name='search'),
    path('api/v1/export_dep/<int:pk>', rolesDepartmentToExcel, name='export department'),
    path('api/v1/export_user/<int:pk>', rolesUserToExcel, name='export user'),
]
