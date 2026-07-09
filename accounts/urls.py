from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('auth/google/login/', views.google_login, name='google_login'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),
    path('logout/', views.logout_view, name='logout'),
]