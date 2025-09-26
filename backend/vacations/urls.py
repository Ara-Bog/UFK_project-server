from django.urls import path
import vacations.views as views

urlpatterns = [
    path('api/vacations/', views.ListVacationsAPIView.as_view(), name="vacations_list"),
    path('api/vacations/<int:pk>', views.VacationAPIView.as_view(), name="vacation"),
    path('api/responsibles', views.get_responsibles, name='get_responsibles'),
    path('api/managers', views.get_managers, name='get_managers'),
    path('api/check_correct', views.check_correct_tab_number, name='check_correct'),
    path('api/take_to_work', views.take_to_work, name='take_to_work'),
    path('api/upload_tab_numbers', views.upload_tab_number, name='load_tab_numbers'),
    path('api/users/current-detail/', views.get_current_user_info, name='user_info'),
    path('api/users/user-settings/', views.UserSettingsAPIView.as_view(), name='user_settings'),
    path('api/users', views.UsersAPIView.as_view(), name='list_users'),
    path('api/users/<int:pk>', views.UserPageAPIView.as_view(), name='page_user'),
    path('api/users/<int:pk>/vacations', views.get_userifno_doc, name='user_infodoc'),
    path('api/templates/', views.FillVacationsAPIView.as_view(), name='templates'),
    path('api/transfer', views.TransferAPIView.as_view(), name='transactions_create'),
    path('api/transfer/<int:pk>', views.TransferAPIView.as_view(), name='transactions_deail'),
    path('api/load_docs_employee', views.load_docs_employee, name='load_docs_employee'),
    path('api/user_periods/<int:pk>', views.UserPeriodsAPIView.as_view(), name='user_periods'),
    path('api/load_plan/', views.load_plan, name="load_plan"),
    path('api/test', views.test, name="test"),
]
