from django.contrib import admin
from teambeat.models import (
    Organization,
    OrganizationInvitation,
    OrganizationUser,
    Team,
    TeamAdmin,
    TeamMember,
    TeamMemberStatus
)

admin.site.register(Organization)
admin.site.register(OrganizationUser)
admin.site.register(OrganizationInvitation)
admin.site.register(Team)
admin.site.register(TeamAdmin)
admin.site.register(TeamMember)
admin.site.register(TeamMemberStatus)
