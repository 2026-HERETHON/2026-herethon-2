from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include

app_name = 'mypage'

urlpatterns = [
    path('', views.mypage_dashboard, name='dashboard'),
    path('cancel/<int:application_id>/', views.cancel_application, name='cancel_application'),
    path('returnship/<int:returnship_id>/', views.respond_returnship, name='respond_returnship'),
    path('conditions/update/', views.work_conditions, name='work_conditions'),
]