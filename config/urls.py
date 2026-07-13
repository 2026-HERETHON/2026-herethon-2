from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('company/', include('company.urls')),
    path('worker/', include('worker.urls')),
    path('mypage/', include('mypage.urls')),
]