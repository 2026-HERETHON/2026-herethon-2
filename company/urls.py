from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/manage/', views.project_manage, name='project_manage'),
]