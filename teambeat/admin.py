from django.contrib import admin
from teambeat.models import (
    Team,
    TeamAdmin,
    TeamMember,
    TeamMemberStatus
)

admin.site.register(Team)
admin.site.register(TeamAdmin)
admin.site.register(TeamMember)
admin.site.register(TeamMemberStatus)
