from django.contrib import admin
from .models import (
    JobCategory,
    Skill,
    JobSkill,
    TimeSlot,
    HiddenAbility,
    JobHiddenAbility,
)

admin.site.register(JobCategory)
admin.site.register(Skill)
admin.site.register(JobSkill)
admin.site.register(TimeSlot)
admin.site.register(HiddenAbility)
admin.site.register(JobHiddenAbility)
