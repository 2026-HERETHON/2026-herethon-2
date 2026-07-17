from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('auth/google/', views.google_login, name='google_login'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),
    path('role-select/', views.role_select, name='role_select'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_redirect, name='home'),
]