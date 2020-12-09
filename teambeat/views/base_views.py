from django.template import loader
from django.views import View
from django.conf import settings

from teambeat.models import (
    Organization,
    Team,
    TeamAdmin,
)

from teambeat.forms import SearchUsersForm


class AuthenticatedView(View):
    def setup(self, request, *args, **kwargs):
        super(AuthenticatedView, self).setup(request, *args, **kwargs)
        self.user = request.user
        has_alerts = False
        org_invitations = self.user.organizationinvitation_set.all()
        if org_invitations:
            has_alerts = True
        self.context = {
            'user': self.user,
            'has_alerts': has_alerts
        }


class TeamBeatView(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(TeamBeatView, self).setup(request, *args, **kwargs)
        organization_uuid = request.session.get('organization')
        if organization_uuid:
            self.organization = Organization.objects.get(uuid=organization_uuid)
            self.org_user = self.organization.organizationuser_set.get(
                user=self.user
            )
            if kwargs.get('team_uuid'):
                self.team = Team.objects.get(
                    organization=self.organization,
                    uuid=kwargs['team_uuid']
                )
                request.session['current_team_id'] = str(self.team.uuid)


class OrganizationAdminView(TeamBeatView):
    def setup(self, request, *args, **kwargs):
        super(OrganizationAdminView, self).setup(request, *args, **kwargs)
        if not self.org_user.is_organization_admin:
            self.context.update({
                'status_code': 403,
                'error_message': (
                    'Access denied for this page. You are not an admin for '
                    'this organization'
                ),
            })
            self.template = loader.get_template(settings.DEFAULT_ERROR_TEMPLATE)
            self.status_code = 403
        else:
            self.status_code = 200


class TeamAdminView(TeamBeatView):
    def setup(self, request, *args, **kwargs):
        super(TeamAdminView, self).setup(request, *args, **kwargs)
        try:
            self.teamadmin = TeamAdmin.objects.get(
                team=self.team,
                organization_user=self.org_user
            )
            self.template = loader.get_template(
                'teambeat/team-admin-dashboard.html'
            )

            self.context.update({
                'current_user': self.org_user,
                'team': self.team,
                'teammembers': self.team.teammember_set.filter(active=True),
                'team_lead': self.team.team_lead,
                'team_admins': self.team.teamadmin_set,
                'user_search_form': SearchUsersForm(),
            })
            self.status_code = 200
        except TeamAdmin.DoesNotExist:
            self.context.update({
                'status_code': 403,
                'error_message': (
                    'Access denied for this page. You are not an admin for '
                    'this team'
                ),
            })
            self.template = loader.get_template(settings.DEFAULT_ERROR_TEMPLATE)
            self.status_code = 403
