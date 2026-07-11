from django.urls import path

from . import views

app_name = 'worker'

urlpatterns = [
    path('onboarding/step1/', views.onboarding_step1, name='onboarding_step1'),
    path('onboarding/step2/', views.onboarding_step2, name='onboarding_step2'),
    path('onboarding/step3/', views.onboarding_step3, name='onboarding_step3'),
    path('onboarding/step4/', views.onboarding_step4, name='onboarding_step4'),
    path('results/hidden-ability/', views.hidden_ability_result, name='hidden_ability_result'),
    path('results/match-top3/', views.match_top3_result, name='match_top3_result'),
    path('projects/', views.project_list, name='project_list'),
]