from django.contrib import admin
from .models import Project, ProjectSkill, ProjectCoreTime, ProjectPreferredScale, ProjectHiddenAbility, Application, ApplicationFile, Returnship

admin.site.register(Project)
admin.site.register(ProjectSkill)
admin.site.register(ProjectCoreTime)
admin.site.register(ProjectPreferredScale)
admin.site.register(ProjectHiddenAbility)
admin.site.register(Application)
admin.site.register(ApplicationFile)
admin.site.register(Returnship)