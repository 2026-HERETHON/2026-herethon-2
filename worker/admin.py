from django.contrib import admin
from .models import (
    WorkerProfile,
    WorkerSkill,
    WorkerHiddenActivity,
    WorkerCoreTime,
    WorkerPreferredScale,
    WorkerConcern,
)

admin.site.register(WorkerProfile)
admin.site.register(WorkerSkill)
admin.site.register(WorkerHiddenActivity)
admin.site.register(WorkerCoreTime)
admin.site.register(WorkerPreferredScale)
admin.site.register(WorkerConcern)
