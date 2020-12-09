from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse

from teambeat.forms import (
    SearchUsersForm,
)
from teambeat.models import (
    Organization,
    OrganizationUser,
    Team,
    TeamMember,
    TeamMemberStatus
)
from teambeat.status_defs import STATUSES
from teambeat.views.base_views import (
    AuthenticatedView,
    TeamBeatView
)
from session_manager.forms import UserProfileForm


class UserSearchAPI(TeamBeatView):
    def get(self, request, *args, **kwargs):
        context = {
            'status': None,
            'searchResult': []
        }
        form = SearchUsersForm(request.GET)
        if form.is_valid():
            context['status'] = 'success'
            org_users = OrganizationUser.search(
                self.organization,
                request.GET['search_term']
            )
            for user in org_users:
                context['searchResult'].append({
                    'displayName': '{} {}'.format(
                        user.first_name,
                        user.last_name
                    ),
                    'email': user.email,
                    'id': user.pk
                })
        else:
            context['status'] = 'Form error'
        return JsonResponse(context)


class Profile(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(Profile, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('teambeat/profile.html')
        if request.session.get('organization'):
            self.current_organization = Organization.objects.filter(
                uuid=request.session['organization']).first()
        else:
            self.current_organization = None
        self.context.update({
            'org_invitations': self.user.organizationinvitation_set.all()
        })

    def get(self, request, *args, **kwargs):
        profile_form = UserProfileForm(
            initial={
                'username': self.request.user.email,
                'email': self.request.user.email,
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'user_id': self.request.user.pk,
            }
        )
        self.context.update({
            'profile_form': profile_form,
            'user_organizations': self.user.organizationuser_set.all(),
            'current_organization': self.current_organization,
            'org_select_submit_text': 'Switch Organization'
        })
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        profile_form = UserProfileForm(request.POST)

        self.context.update({
            'profile_form': profile_form,
            'user_organizations': self.user.organizationuser_set.all(),
            'current_organization': self.current_organization,
            'org_select_submit_text': 'Switch Organization'
        })
        if 'update-profile' in request.POST:
            if profile_form.is_valid():
                user = User.objects.get(pk=self.request.user.pk)
                user.username = request.POST['email']
                user.email = request.POST['email']
                user.first_name = request.POST['first_name']
                user.last_name = request.POST['last_name']
                user.save()
                messages.success(request, 'Profile updated.')
                return redirect(reverse('session_manager_profile'))
            else:
                self.context['form'] = profile_form

        elif 'organization_id' in request.POST:
            org_id = request.POST['organization_id']
            organization = Organization.objects.get(pk=org_id)
            request.session['organization'] = str(organization.uuid)
            return redirect(reverse('session_manager_profile'))

        return HttpResponse(self.template.render(self.context, request))


class SetOrganization(TeamBeatView):
    def setup(self, request, *args, **kwargs):
        super(SetOrganization, self).setup(request, *args, **kwargs)
        self.context.update({
            'user_organizations': request.user.organizationuser_set.all(),
            'current_organization': None,
            'org_select_submit_text': 'Select Organization'
        })

        self.template = loader.get_template('teambeat/set_organization.html')

    def get(self, request, *args, **kwargs):
        user_organizations = OrganizationUser.objects.filter(user=request.user)
        if user_organizations.count() == 1:
            request.session['organization'] = str(
                user_organizations.first().organization.uuid
            )
            return redirect('dashboard')
        else:
            return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        org_id = request.POST['organization_id']
        organization = Organization.objects.get(pk=org_id)
        request.session['organization'] = str(organization.uuid)
        return redirect(reverse('dashboard'))


class SetStatus(TeamBeatView):
    def setup(self, request, *args, **kwargs):
        super(SetStatus, self).setup(request, *args, **kwargs)
        self.teammember = TeamMember.objects.get(
            team=self.team,
            organization_user=self.org_user
        )
        self.template = loader.get_template('teambeat/set_status.html')
        self.context.update({
            'status_options': STATUSES,
        })

    def get(self, request, *args, **kwargs):
        todays_status = self.teammember.status_for_today
        self.context['existing_status'] = todays_status
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        todays_status = self.teammember.status_for_today
        if not todays_status:
            todays_status = TeamMemberStatus(teammember=self.teammember)
            success_message = 'Thank you for setting your {} status!'.format(
                self.team.name
            )
        else:
            success_message = 'Your {} status for today has been updated'.format(
                self.team.name
            )
        todays_status.status = request.POST['selected-status']
        todays_status.additional_info_for_team = request.POST['status-additional-info-team']
        todays_status.additional_info_for_lead = request.POST['status-additional-info-lead']
        todays_status.save()
        messages.success(request, success_message)
        return redirect(reverse('dashboard'))


class Dashboard(TeamBeatView):
    def get(self, request, *args, **kwargs):
        if not request.session.get('organization'):
            return redirect(reverse('set_organization'))
        template = loader.get_template('teambeat/dashboard.html')
        self.context.update({
            'org_user': self.org_user,
            'myteams': self.org_user.teammember_set.all(),
            'adminteams': self.org_user.teamadmin_set.all(),
            'leadteams': self.org_user.teamlead_teams,
            'organization': self.organization
        })
        return HttpResponse(template.render(self.context, request))


class DashboardAPI(TeamBeatView):
    def _formatted_admin_teams(self):
        admin_teams = []
        for teamlead in self.org_user.teamlead_set.all():
            admin_teams.append(
                {
                    'teamId': teamlead.team.pk,
                    'teamName': teamlead.team.name
                }
            )
        return admin_teams

    def _formatted_teams(self):
        teams = []
        for teammember in self.org_user.teammember_set.all():
            teams.append(
                {
                    'teamId': teammember.team.pk,
                    'teamName': teammember.team.name,
                    'status': teammember.status_for_today
                }
            )
        return teams

    def get(self, request, *args, **kwargs):
        context = {
            'adminTeams': self._formatted_admin_teams(),
            'teams': self._formatted_teams()
        }
        return JsonResponse(context)
