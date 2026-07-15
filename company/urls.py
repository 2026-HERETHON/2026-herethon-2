from django.urls import path

from . import views

app_name = 'company'

urlpatterns = [
    path('onboarding/', views.company_onboarding, name='onboarding'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/manage/', views.project_manage, name='project_manage'),
    
    path('projects/<int:project_id>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:project_id>/start/', views.project_start, name='project_start'),
    path('projects/<int:project_id>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:project_id>/complete/', views.project_complete, name='project_complete'),
    path('projects/<int:project_id>/applicants/', views.project_applicants, name='project_applicants'),
    path(
        'projects/<int:project_id>/applicants/<int:application_id>/',
        views.project_applicant_detail,
        name='project_applicant_detail',
    ),
    path(
        'projects/<int:project_id>/applicants/<int:application_id>/decide/',
        views.application_decide,
        name='application_decide',
    ),
    path(
        'projects/<int:project_id>/applicants/<int:application_id>/returnship/',
        views.returnship_create,
        name='returnship_create',
    ),
    path('projects/<int:project_id>/', views.project_progress_detail, name='project_progress_detail'),
]