from django.contrib import admin

from employee_management_backend.companies.models import Team, TeamMember

admin.site.register(Team)
admin.site.register(TeamMember)
