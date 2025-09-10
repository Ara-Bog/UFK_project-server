from django.urls import path
import court_cases.views as views

urlpatterns = [
    path('api/notifies/', views.NotifiesAPI.as_view()),
    path('api/users/current-detail/',views.get_current_user_info, name='user_info'),
    path('api/courts/', views.CourtsListAPI.as_view()),
    path('api/courts/create/', views.CourtSelfAPI.as_view()),
    path('api/courts/excel/', views.create_excel, name="get excel"),
    path('api/court/<int:pk>/', views.CourtSelfAPI.as_view()),
    path('api/court/<int:pk>/event', views.EventSelfAPI.as_view()),
    path('api/load_courts/', views.load_excel, name='load_excel'),
]
