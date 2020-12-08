from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, redirect, resolve_url
from django.template import loader
from django.views import View
from django.urls import reverse

from urllib.parse import urlparse

from session_manager.forms import (
    CreateUserForm,
    LoginUserForm,
    ResetPasswordForm,
    UserProfileForm
)

from session_manager.models import SessionManager, UserToken


class CreateUserView(View):
    """ Views for a new user registration
    """
    def setup(self, request, *args, **kwargs):
        super(CreateUserView, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('session_manager/register.html')
        self.context = {}

    def get(self, request, *args, **kwargs):
        form = CreateUserForm()
        self.context.update({
            'form': form,
        })
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = SessionManager.create_user(
                email=request.POST['email'],
                password=request.POST['password'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name']
            )
            messages.success(request, 'Registration complete! Please log in to continue.')
            return redirect(reverse('session_manager_login'))
        else:
            self.context.update({
                'form': form,
            })
            return HttpResponse(self.template.render(self.context, request))


class LoginUserView(View):
    """ Views for logging in an existing user, either via form post
        or token URL
    """
    def setup(self, request, *args, **kwargs):
        super(LoginUserView, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('session_manager/login.html')
        self.context = {}

    def get(self, request, *args, **kwargs):
        # check if a login token was provided
        if request.GET.get('token') and request.GET.get('user'):
            token, token_error_message = UserToken.get_token(token=request.GET['token'], username=request.GET['user'], token_type='login')
            if token:
                if token.is_valid:
                    # a valid token/user combination was given, so log in and delete the token
                    login(request, token.user)
                    token.delete()
                    request.session['user_is_authenticated'] = True
                    return redirect(reverse(settings.LOGIN_SUCCESS_REDIRECT))
                else:
                    # provided token was found, but it is expired
                    # clean up the token
                    token.delete()
                    messages.error(request, 'Token is expired.')
            else:
                # no matching token was found for provided user/token
                messages.error(request, token_error_message)

        # no token was provided, or it was invalid, so just render the login form
        form = LoginUserForm()
        self.context.update({
            'form': form,
        })
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        # we should only get here if they submitted the form instead of a token in the URL
        # standard Django form handling here
        form = LoginUserForm(request.POST)
        if form.is_valid():
            user, error_reason = SessionManager.check_user_login(
                username_or_email=request.POST['email'],
                password=request.POST['password']
            )
            if not user:
                messages.error(request, error_reason)
                self.context.update({
                    'form': form,
                })
                return HttpResponse(self.template.render(self.context, request))
            else:
                login(request, user)
                request.session['user_is_authenticated'] = True
                if request.session.get('login_redirect_from'):
                    return redirect(request.session.get('login_redirect_from'))
                else:
                    return redirect(reverse(settings.LOGIN_SUCCESS_REDIRECT))
        else:
            messages.error(request, 'Something went wrong. Please correct errors below.')
            self.context.update({
                'form': form,
            })
            return HttpResponse(self.template.render(self.context, request))


class ResetPasswordWithTokenView(View):
    """ View that allows a user to reset their password via a token,
        without needing to log in
    """
    def setup(self, request, *args, **kwargs):
        super(ResetPasswordWithTokenView, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('session_manager/reset_password.html')
        self.context = {}
        # get the token and error message, needed for both GET and POST
        self.token, self.token_error_message = UserToken.get_token(
            token=request.GET.get('token'),
            username=request.GET.get('user'),
            token_type='reset'
        )

    def get(self, request, *args, **kwargs):
        # If we find a valid token, show the reset form with the user's ID passed to it
        if self.token:
            if self.token.is_valid:
                form = ResetPasswordForm(initial={'user_id': self.token.user.id})
                self.context.update({'form': form})
            else:
                messages.error(request, 'Token is expired.')
        else:
            messages.error(request, self.token_error_message)
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = ResetPasswordForm(request.POST)
        # if a valid token was given and the form is valid, reset user's password
        # and redirect to login
        if self.token:
            if self.token.is_valid:
                if form.is_valid():
                    user = SessionManager.get_user_by_id(request.POST['user_id'])
                    user.set_password(request.POST['password'])
                    user.save()
                    messages.success(request, 'Password reset. Please log in to continue.')
                    self.token.delete()
                    return redirect(reverse('session_manager_login'))
            else:
                messages.error(request, 'Token is expired.')
        else:
            messages.error(request, self.token_error_message)
        self.context.update({'form': form})
        return HttpResponse(self.template.render(self.context, request))


class ResetPasswordFromProfileView(View):
    """ View that allows a user to reset their password when logged in
    """
    def setup(self, request, *args, **kwargs):
        super(ResetPasswordFromProfileView, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('session_manager/reset_password.html')
        self.context = {
            'breadcrumbs': [
                ('Profile', reverse('session_manager_profile')),
                ('Reset Password', None)
            ]
        }

    def get(self, request, *args, **kwargs):
        form = ResetPasswordForm(initial={'user_id': self.request.user.id})
        self.context.update({'form': form})
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = self.request.user
            user.set_password(request.POST['password'])
            user.save()
            messages.success(request, 'Your password has been reset. Please log in again to continue.')
            return redirect(reverse(settings.PW_RESET_SUCCESS_REDIRECT))
        self.context.update({'form': form})
        return HttpResponse(self.template.render(self.context, request))


class LogOutUserView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'Logged out.')
        request.session['user_is_authenticated'] = False
        return redirect(reverse('session_manager_login'))


class Index(View):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('session_manager/index.html')
        form = UserProfileForm(
            initial={
                'username': self.request.user.username,
                'email': self.request.user.email,
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'user_id': self.request.user.pk,
            }
        )
        context = {
            'form': form,
        }
        return HttpResponse(template.render(context, request))

    def post(self, request, *args, **kwargs):
        template = loader.get_template('session_manager/index.html')
        form = UserProfileForm(request.POST)

        if form.is_valid():
            user = User.objects.get(pk=self.request.user.pk)
            user.username = request.POST['username']
            user.email = request.POST['email']
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.save()
            messages.success(request, 'Profile updated.')
            return redirect(reverse('session_manager_profile'))
        else:
            context = {
                'form': form,
            }
            return HttpResponse(template.render(context, request))



