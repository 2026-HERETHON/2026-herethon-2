from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('WORKER', '경력자'),
        ('COMPANY', '기업'),
    ]

    google_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    profile_image_url = models.URLField(max_length=500, null=True, blank=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.email
