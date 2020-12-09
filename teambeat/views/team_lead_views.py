from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from teambeat.models import Team
from teambeat.views.base_views import TeamBeatView


class TeamLeadDashboard(TeamBeatView):
    def setup(self, request, *args, **kwargs):
        super(TeamLeadDashboard, self).setup(request, *args, **kwargs)
        try:
            self.is_team_lead = Team.objects.get(
                pk=self.team.pk,
                team_lead=self.org_user
            )

            self.template = loader.get_template('teambeat/team-lead-status-view.html')
            self.context.update({'statuses': self.team.teamstatus_set})
            self.status_code = 200
        except Team.DoesNotExist:
            self.context.update({
                'status_code': 403,
                'error_message': (
                    'Access denied for this page. You are not a Team Lead '
                    'for this team',
                )
            })
            self.template = loader.get_template(
                settings.DEFAULT_ERROR_TEMPLATE
            )
            self.status_code = 403

    def get(self, request, *args, **kwargs):
        return HttpResponse(
            self.template.render(self.context, request),
            status=self.status_code
        )
