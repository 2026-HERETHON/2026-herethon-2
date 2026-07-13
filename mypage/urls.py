from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('applications/', views.application_status, name='application_status'),
    path('applications/<int:application_id>/cancel/', views.cancel_application, name='cancel_application'),
    path('returnship-offers/', views.returnship_offers, name='returnship_offers'),
    path('returnship-offers/<int:returnship_id>/respond/', views.respond_returnship, name='respond_returnship'),
    path('work-conditions/', views.work_conditions, name='work_conditions'),
]