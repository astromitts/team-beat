from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views import View
from django.urls import reverse

from teambeat.models import (
    Organization,
    OrganizationUser,
    Team,
    TeamAdmin,
    TeamMember,
    TeamMemberStatus,
)
from teambeat.forms import (
    AddUserEmailForm,
    AddUserNameForm,
    TeamForm,
    SearchUsersForm,
    RemoveTeamMemberForm,
    SetOrganizationForm,
)
from teambeat.status_defs import STATUSES
from session_manager.models import SessionManager
from session_manager.forms import UserProfileForm


class Profile(View):
    def setup(self, request, *args, **kwargs):
        super(Profile, self).setup(request, *args, **kwargs)
        self.user = request.user
        self.template = loader.get_template('teambeat/profile.html')
        self.current_organization = Organization.objects.filter(
            uuid=request.session['organization']).first()

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
        context = {
            'profile_form': profile_form,
            'user_organizations': self.user.organizationuser_set.all(),
            'current_organization': self.current_organization,
            'org_select_submit_text': 'Switch Organization'
        }
        return HttpResponse(self.template.render(context, request))

    def post(self, request, *args, **kwargs):
        profile_form = UserProfileForm(request.POST)

        context = {
            'profile_form': profile_form,
            'user_organizations': self.user.organizationuser_set.all(),
            'current_organization': self.current_organization,
            'org_select_submit_text': 'Switch Organization'
        }
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
                context['form'] = profile_form

        elif 'organization_id' in request.POST:
            org_id = request.POST['organization_id']
            organization = Organization.objects.get(pk=org_id)
            request.session['organization'] = str(organization.uuid)
            return redirect(reverse('session_manager_profile'))

        return HttpResponse(self.template.render(context, request))


class TeamBeatView(View):
    def setup(self, request, *args, **kwargs):
        super(TeamBeatView, self).setup(request, *args, **kwargs)
        user = self.request.user
        organization_uuid = request.session.get('organization')
        if organization_uuid:
            self.organization = Organization.objects.get(uuid=organization_uuid)
            self.user = self.organization.organizationuser_set.get(
                user=user
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
        if not self.user.is_organization_admin:
            self.context = {
                'status_code': 403,
                'error_message': (
                    'Access denied for this page. You are not an admin for '
                    'this organization'
                ),
            }
            self.template = loader.get_template(settings.DEFAULT_ERROR_TEMPLATE)
            self.status_code = 403
        else:
            self.status_code = 200


class AddUserToOrganization(OrganizationAdminView):
    def setup(self, request, *args, **kwargs):
        super(AddUserToOrganization, self).setup(request, *args, **kwargs)

        if self.status_code == 200:
            self.template = loader.get_template('teambeat/generic_form.html')
            self.form = AddUserEmailForm
            self.context = {
                'header': 'Add a user to organization "{}"'.format(self.organization.name),
                'submit_text': 'Add user',
                'additional_helptext': None,
                'form': self.form()
            }

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            if 'first_name' not in request.POST:
                django_user = SessionManager.get_user_by_username(request.POST['email'])
                if django_user:
                    existing_org_user = OrganizationUser.objects.filter(
                        organization=self.organization,
                        user=django_user
                    ).first()
                    if existing_org_user and existing_org_user.active == True:
                        messages.error(request, 'This user is already in your organization')
                        self.context['form'] = form
                        return HttpResponse(self.template.render(self.context, request))
                    elif existing_org_user:
                        existing_org_user.active = True
                        existing_org_user.save()
                        messages.success(request, 'Added {} to organization'.format(existing_org_user.display_name))
                        if request.session.get('current_team_id'):
                            return redirect(reverse('team_admin_dashboard', kwargs={'team_uuid': request.session.get('current_team_id')}))
                        return redirect(reverse('organization_admin_dashboard'))
                else:
                    self.context['form'] = AddUserNameForm(initial={'email': request.POST['email']})
                    return HttpResponse(self.template.render(self.context, request))
            else:
                django_user = SessionManager.create_user(
                    email=request.POST['email'],
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name']
                )
                org_user = OrganizationUser(
                    organization=self.organization,
                    user=django_user
                )
                org_user.save()
                messages.success(request, 'Added {} to organization'.format(org_user.display_name))
                if request.session.get('current_team_id'):
                    return redirect(reverse('team_admin_dashboard', kwargs={'team_uuid': request.session.get('current_team_id')}))
                return redirect(reverse('organization_admin_dashboard'))

        self.context['form'] = form
        return HttpResponse(self.template.render(self.context, request))


class OrganizationAdminDashboard(OrganizationAdminView):
    def setup(self, request, *args, **kwargs):
        super(OrganizationAdminDashboard, self).setup(request, *args, **kwargs)

        if self.status_code == 200:
            request.session['current_team_id'] = None
            self.template = loader.get_template('teambeat/organization-admin-dashboard.html')
            self.context = {
                'organization': self.organization,
                'org_users': self.organization.organizationuser_set.filter(active=True).all(),
                'current_user': self.user,
            }

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.template.render(self.context, request))

class OrganizationAdminDashboardAPI(OrganizationAdminView):
    def post(self, request, *args, **kwargs):
        if kwargs['api_target'] == 'removeuser':
            org_user = OrganizationUser.objects.get(pk=request.POST['orguser_id'])
            org_user.active = False
            org_user.teammember_set.all().update(active=False)
            org_user.save()
            context = {'status': 'success'}
        if kwargs['api_target'] == 'toggleisadmin':
            org_user = OrganizationUser.objects.get(pk=request.POST['orguser_id'])
            if org_user.is_organization_admin:
                org_user.is_organization_admin = False
            else:
                org_user.is_organization_admin = True
            org_user.save()
            context = {'status': 'success'}

        return JsonResponse(context)


class SelectOrganization(TeamBeatView):
    def setup(self, request, *args, **kwargs):
        super(SelectOrganization, self).setup(request, *args, **kwargs)
        self.context = {
            'user_organizations': request.user.organizationuser_set.all(),
            'current_organization': None,
            'org_select_submit_text': 'Select Organization'
        }

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



class Dashboard(TeamBeatView):
    def get(self, request, *args, **kwargs):
        if not request.session.get('organization'):
            return redirect(reverse('set_organization'))
        template = loader.get_template('teambeat/dashboard.html')
        context = {
            'org_user': self.user,
            'myteams': self.user.teammember_set.all(),
            'adminteams': self.user.teamadmin_set.all(),
            'leadteams': self.user.teamlead_set.all(),
            'organization': self.organization
        }
        return HttpResponse(template.render(context, request))


class DashboardAPI(TeamBeatView):
    def _formatted_admin_teams(self):
        admin_teams = []
        for teamlead in self.user.teamlead_set.all():
            admin_teams.append(
                {
                    'teamId': teamlead.team.pk,
                    'teamName': teamlead.team.name
                }
            )
        return admin_teams

    def _formatted_teams(self):
        teams = []
        for teammember in self.user.teammember_set.all():
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


class CreateTeam(TeamBeatView):
    def setup(self, request, *args, **kwargs):
        super(CreateTeam, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('teambeat/generic_form.html')
        self.form = TeamForm
        self.context = {
            'header': 'Create a Team',
            'submit_text': 'Create Team',
            'additional_helptext': (
                'You will automatically be set as an admin of any teams you'
                ' create. You can add other admins and/or remove yourself as '
                'an admin later.'
            )
        }

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
                team.team_lead = self.user
            team.save()

            if request.POST['creator_is_member'] == 'Y':
                team_member = TeamMember(
                    organization_user=self.user,
                    team=team
                )
                team_member.save()

            team_admin = TeamAdmin(
                organization_user=self.user,
                team=team
            )
            team_admin.save()
            messages.success(request, 'Team "{}" created'.format(team.name))
            return redirect(reverse('dashboard'))
        else:
            self.context['form'] = form
        return HttpResponse(self.template.render(self.context, request))

class SetStatus(TeamBeatView):
    def setup(self, request, *args, **kwargs):
        super(SetStatus, self).setup(request, *args, **kwargs)
        self.teammember = TeamMember.objects.get(
            team=self.team,
            organization_user=self.user
        )
        self.template = loader.get_template('teambeat/set_status.html')
        self.context = {
            'status_options': STATUSES,
        }

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


class TeamLeadDashboard(TeamBeatView):
    def setup(self, request, *args, **kwargs):
        super(TeamLeadDashboard, self).setup(request, *args, **kwargs)
        try:
            self.is_team_lead = Team.objects.get(
                pk=self.team.pk,
                team_lead=self.user
            )

            self.template = loader.get_template('teambeat/team-lead-status-view.html')
            self.context = {'statuses': self.team.teamstatus_set}
            self.status_code = 200
        except Team.DoesNotExist:
            self.context = {
                'status_code': 403,
                'error_message': (
                    'Access denied for this page. You are not a Team Lead '
                    'for this team',
                )
            }
            self.template = loader.get_template(
                settings.DEFAULT_ERROR_TEMPLATE
            )
            self.status_code = 403

    def get(self, request, *args, **kwargs):
        return HttpResponse(
            self.template.render(self.context, request),
            status=self.status_code
        )

class TeamAdminView(TeamBeatView):
    def setup(self, request, *args, **kwargs):
        super(TeamAdminView, self).setup(request, *args, **kwargs)
        try:
            self.teamadmin = TeamAdmin.objects.get(
                team=self.team,
                organization_user=self.user
            )
            self.template = loader.get_template(
                'teambeat/team-admin-dashboard.html'
            )

            self.context = {
                'current_user': self.user,
                'team': self.team,
                'teammembers': self.team.teammember_set.filter(active=True),
                'team_lead': self.team.team_lead,
                'team_admins': self.team.teamadmin_set,
                'user_search_form': SearchUsersForm(),
            }
            self.status_code = 200
        except TeamAdmin.DoesNotExist:
            self.context = {
                'status_code': 403,
                'error_message': (
                    'Access denied for this page. You are not an admin for '
                    'this team'
                ),
            }
            self.template = loader.get_template(settings.DEFAULT_ERROR_TEMPLATE)
            self.status_code = 403


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
            context['status'] = 'error'
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
                pk=request.POST['teamadmin_id']).exclude(organization_user=self.user)
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


