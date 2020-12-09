from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse

from teambeat.forms import TeamForm, RemoveTeamMemberForm
from teambeat.models import (
    OrganizationUser,
    Team,
    TeamAdmin,
    TeamMember
)
from teambeat.views.base_views import TeamAdminView, TeamBeatView


class CreateTeam(TeamBeatView):
    def setup(self, request, *args, **kwargs):
        super(CreateTeam, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('teambeat/generic_form.html')
        self.form = TeamForm
        self.context.update({
            'header': 'Create a Team',
            'submit_text': 'Create Team',
            'additional_helptext': (
                'You will automatically be set as an admin of any teams you'
                ' create. You can add other admins and/or remove yourself as '
                'an admin later.'
            )
        })

    def get(self, request, *args, **kwargs):
        form = self.form()
        self.context['form'] = form
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            team = Team(
                name=request.POST['name'],
                organization=self.organization
            )

            if request.POST['creator_is_lead'] == 'Y':
                team.team_lead = self.org_user
            team.save()

            if request.POST['creator_is_member'] == 'Y':
                team_member = TeamMember(
                    organization_user=self.org_user,
                    team=team
                )
                team_member.save()

            team_admin = TeamAdmin(
                organization_user=self.org_user,
                team=team
            )
            team_admin.save()
            messages.success(request, 'Team "{}" created'.format(team.name))
            return redirect(reverse('dashboard'))
        else:
            self.context['form'] = form
        return HttpResponse(self.template.render(self.context, request))


class TeamAdminDashboard(TeamAdminView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(self.template.render(self.context, request))


class TeamAdminDashboardAPI(TeamAdminView):
    def setup(self, request, *args, **kwargs):
        super(TeamAdminDashboardAPI, self).setup(request, *args, **kwargs)
        self.context = {
            'status_code': self.status_code,
            'errorMessage': self.context.get('error_message'),
            'status': ''
        }

    def _get_or_create_team_admin(self, org_user):
        team_admin = self.team.teamadmin_set.filter(organization_user=org_user).first()
        created = False
        if not team_admin:
            team_admin = TeamAdmin(
                organization_user=org_user,
                team=self.team
            )
            team_admin.save()
            created = True
        return (team_admin, created)

    def post(self, request, *args, **kwargs):
        api_target = kwargs['api_target']
        if self.status_code == 403:
            self.context['status'] = 'error'
            return JsonResponse(self.context, status=self.status_code)
        if api_target == 'removeteammember':
            form = RemoveTeamMemberForm(request.POST)
            if form.is_valid():
                TeamMember.objects.filter(
                    pk=request.POST['teammember_id']).update(active=False)
                self.context['status'] = 'success'
            else:
                self.context['status'] = 'error'
                self.context['errorMessage'] = 'Could not complete request: invalid form'
        elif api_target == 'addteammember':
                org_user = OrganizationUser.objects.get(pk=request.POST['user_id'])
                teammember_qs = self.team.teammember_set.filter(
                    organization_user=org_user)
                if teammember_qs.exists() and teammember_qs.first().active:
                    self.context['errorMessage']  = 'User already in team.'
                else:
                    if teammember_qs.exists():
                        new_teammember = teammember_qs.first()
                        new_teammember.active = True
                        new_teammember.save()
                    else:
                        new_teammember = TeamMember(
                            organization_user=org_user,
                            team=self.team
                        )
                        new_teammember.save()
                    rendered_table_row = loader.render_to_string(
                        'teambeat/includes/team-admin-dashboard/teammember-row.html',
                        context={'teammember': new_teammember, 'team': self.team},
                        request=request
                    )
                    self.context['status'] = 'success'
                    self.context['teamMemberId'] = new_teammember.pk
                    self.context['htmlResult'] = rendered_table_row

        elif api_target == 'addteamadmin':
                org_user = OrganizationUser.objects.get(pk=request.POST['user_id'])
                new_teamadmin, created = self._get_or_create_team_admin(org_user)
                if created:
                    rendered_table_row = loader.render_to_string(
                        'teambeat/includes/team-admin-dashboard/teamadmin-row.html',
                        context={'admin': new_teamadmin, 'team': self.team,},
                        request=request
                    )
                    self.context['status'] = 'success'
                    self.context['teamAdminId'] = new_teamadmin.pk
                    self.context['htmlResult'] = rendered_table_row
                else:
                    self.context['status'] = 'error'
                    self.context['errorMessage'] = 'Could not create team admin instance or user is already admin.'

        elif api_target == 'removeteamadmin':
            teamadmin_qs = self.team.teamadmin_set.filter(
                pk=request.POST['teamadmin_id']).exclude(organization_user=self.org_user)
            if teamadmin_qs.exists():
                teamadmin_qs.first().delete()
                self.context['status'] = 'success'
            else:
                self.context['status'] = 'error'
                self.context['errorMessage'] = (
                    'Admin user not found or is the current user'
                )

        elif api_target == 'changeteamlead':
                org_user = OrganizationUser.objects.get(pk=request.POST['user_id'])
                if org_user:
                    self.team.team_lead = org_user
                    self.team.save()
                    self._get_or_create_team_admin(org_user)

                    rendered_table_row = loader.render_to_string(
                        'teambeat/includes/team-admin-dashboard/teamlead-row.html',
                        context={'team_lead': self.team.team_lead},
                        request=request
                    )
                    self.context['status'] = 'success'
                    self.context['htmlResult'] = rendered_table_row
        return JsonResponse(self.context, status=self.status_code)
