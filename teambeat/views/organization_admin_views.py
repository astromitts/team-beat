from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse

from teambeat.forms import (
    CreateOrganizationForm,
    SearchUsersForm,
    InviteUserForm
)
from teambeat.models import (
    Organization,
    OrganizationInvitation,
    OrganizationUser,
)

from teambeat.views.base_views import (
    AuthenticatedView,
    OrganizationAdminView
)

from session_manager.models import SessionManager


class CreateOrganization(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(CreateOrganization, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('teambeat/generic_form.html')
        self.form = CreateOrganizationForm
        self.context.update({
            'header': 'Create a New Organization',
            'submit_text': 'Submit',
            'additional_helptext': None,
            'form': self.form()
        })

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            new_organization = Organization(name=request.POST['organization_name'])
            new_organization.save()
            new_organization.admins.add(self.user)
            new_organization.save()
            org_user = OrganizationUser(
                user=self.user,
                organization=new_organization,
                is_organization_admin=True
            )
            org_user.save()
            request.session['organization'] = str(new_organization.uuid)
            messages.success(
                request,
                'Created new organization "{}"'.format(new_organization.name)
            )
            return redirect(reverse('organization_admin_dashboard'))
        self.context['form'] = form
        return HttpResponse(self.template.render(self.context, request))


class HandleOrganizationInvitation(AuthenticatedView):
    def post(self, request, *args, **kwargs):
        organization = Organization.objects.filter(
            uuid=self.kwargs['org_uuid'],
        ).first()
        invitation = None
        if not organization:
            messages.error(request, 'Organization not found')
        else:
            invitation = OrganizationInvitation.objects.filter(
                organization=organization,
                user=self.user
            ).first()
            if not invitation:
                messages.error(request, 'Invitation not found')
        if organization and invitation:
            if 'accept-invitation' in request.POST:
                org_user = OrganizationUser.objects.filter(
                    user=self.user,
                    organization=organization
                ).first()
                if org_user:
                    if org_user.active:
                        messages.success(
                            request,
                            'You already part of organization "{}". Invitation dismissed.'.format(
                                organization.name
                            )
                        )
                    else:
                        org_user.active = True
                        org_user.save()
                        messages.success(
                            request,
                            'You have been added to organization "{}"'.format(
                                organization.name
                            )
                        )
                    invitation.delete()
                else:
                    org_user = OrganizationUser(
                        user=self.user,
                        organization=organization
                    )
                    org_user.save()
                    invitation.delete()
                    messages.success(
                        request,
                        'You have been added to organization "{}"'.format(
                            organization.name
                        )
                    )
            elif 'decline-invitation' in request.POST:
                invitation.delete()
                messages.success(
                    request,
                    'Invitation to organization "{}" dismissed.'.format(
                        organization.name
                    )
                )
        return redirect(reverse('session_manager_profile'))


class AddUserToOrganization(OrganizationAdminView):
    def setup(self, request, *args, **kwargs):
        super(AddUserToOrganization, self).setup(request, *args, **kwargs)

        if self.status_code == 200:
            self.template = loader.get_template('teambeat/generic_form.html')
            self.form = SearchUsersForm
            self.context.update({
                'header': 'Add a user to organization "{}"'.format(self.organization.name),
                'submit_text': 'Find user',
                'additional_helptext': None,
                'form': self.form()
            })

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        if 'search_term' in request.POST:
            form = SearchUsersForm(request.POST)
            stage = 1
        elif 'confirmed_invitation' in request.POST:
            stage = 2
        else:
            stage = 3

        if stage == 1:
            django_users = SessionManager.full_search(
                request.POST['search_term']
            )
            self.context.update({
                'search_result_users': django_users,
                'form': InviteUserForm()
            })
            self.template = loader.get_template('teambeat/user-search-confirm-results.html')
            return HttpResponse(self.template.render(self.context, request))
        elif stage == 2:
            django_user = SessionManager.get_user_by_username(request.POST['email'])
            existing_org_user = OrganizationUser.objects.filter(
                organization=self.organization,
                user=django_user
            ).first()
            if existing_org_user and existing_org_user.active == True:
                messages.error(request, 'This user is already in your organization')
                return HttpResponse(self.template.render(self.context, request))
            else:
                org_invitation_exists = OrganizationInvitation.objects.filter(
                    organization=self.organization,
                    user=django_user
                ).first()
                if org_invitation_exists:
                    messages.success(
                        request,
                        '{} already has an invitation to the organization.'.format(
                            org_invitation_exists.display_name)
                    )
                else:
                    org_invitation = OrganizationInvitation(
                        organization=self.organization,
                        user=django_user
                    )
                    org_invitation.save()
                    self.organization.send_org_invitation_email(_to=django_user,_from=self.user)
                    messages.success(request, 'Invited {} to organization'.format(org_invitation.display_name))
            if request.session.get('current_team_id'):
                return redirect(reverse('team_admin_dashboard', kwargs={'team_uuid': request.session.get('current_team_id')}))
            return redirect(reverse('organization_admin_dashboard'))
        elif stage == 3:
            django_user = SessionManager.create_user(
                email=request.POST['email']
            )
            org_invitation = OrganizationInvitation(
                organization=self.organization,
                user=django_user
            )
            org_invitation.save()
            self.organization.send_app_invitation_email(_to=django_user,_from=self.user)
            messages.success(request, 'Invited {} to TeamBeat for your organization'.format(django_user.email))
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
            self.context.update({
                'organization': self.organization,
                'org_users': self.organization.organizationuser_set.filter(active=True).all(),
                'current_user': self.org_user,
                'invited_users': OrganizationInvitation.objects.filter(organization=self.organization)
            })

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
                self.organization.admins.remove(org_user.user)
                self.organization.save()
            else:
                org_user.is_organization_admin = True
                self.organization.admins.add(org_user.user)
                self.organization.save()
            org_user.save()
            context = {'status': 'success'}
        if kwargs['api_target'] == 'cancelinvitation':
            invitation = OrganizationInvitation.objects.filter(
                pk=request.POST['invitee_id']
            ).first()
            if invitation:
                invitation.delete()
            context = {'status': 'success'}
        return JsonResponse(context)
