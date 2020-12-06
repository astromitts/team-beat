from django.forms import (
    ModelForm,
    PasswordInput,
    CharField,
    HiddenInput,
    TextInput,
)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from session_manager.models import SessionManager
from session_manager.utils import special_chars


class CreateUserForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Minimum 3 characters. Letters, numbers, and underscores only.'
        self.fields['password'].help_text = 'Minimum 8 characters. Must contain at least 1 letter, 1 number and 1 special character.'

    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        widgets = {
            'password': PasswordInput(attrs={'class': 'form-control form-control-sm'}),
            'email': TextInput(attrs={'class': 'form-control form-control-sm'}),
            'username': TextInput(attrs={'class': 'form-control form-control-sm'})
        }

    def clean(self):
        """ Enforces username and password requirements
        """
        super(CreateUserForm, self).clean()
        data = self.cleaned_data
        errors = []

        has_alpha = False
        has_number = False
        has_special = False
        clean_password = data['password']
        password_errors = []
        if len(clean_password) < 8:
            password_errors.append('<li>Must be at least 8 characters.</li>')
        for char in clean_password:
            if char.isalpha():
                has_alpha = True
            if char.isnumeric():
                has_number = True
            if char in special_chars:
                has_special = True
        if not has_alpha:
            password_errors.append('<li>Must contain at least one letter.</li>')
        if not has_number:
            password_errors.append('<li>Must contain at least one number.</li>')
        if not has_special:
            password_errors.append(
                '<li>Must contain at least one special character ({}).</li>'.format(
                    ', '.join(special_chars)
                )
            )

        if password_errors:
            errors.append(
                'Invalid password: <ul>{}</ul>'.format(''.join(password_errors))
            )

        clean_username = self.cleaned_data['username']
        username_errors = []
        if len(clean_username) < 3:
            username_errors.append('<li>Must be at least 3 characters.</li>')

        username_invalid_char = False
        for char in clean_username:
            username_invalid_char = not char.isalpha() and not char.isnumeric() and char != '_'

        if username_invalid_char:
            username_errors.append(
                '<li>Letters, numbers, and underscores only, please.</li>'
            )

        user_exists = SessionManager.get_user_by_username(username=clean_username)
        if user_exists:
            username_errors.append(
                '<li>A user with this username already exists.</li>'
            )

        if username_errors:
            errors.append(
                'Invalid username: <ul>{}</ul>'.format(''.join(username_errors))
            )

        if errors:
            raise ValidationError(mark_safe('<br />'.join(errors)))
        return data


class ResetPasswordForm(ModelForm):
    user_id = CharField(widget=HiddenInput())
    class Meta:
        model = User
        fields = ['password', 'user_id']
        widgets = {
            'password': PasswordInput(attrs={'class': 'form-control form-control-sm'}),
            'user_id': HiddenInput()
        }


class LoginUserForm(ModelForm):
    username_or_email = CharField(widget=TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['username_or_email', 'password']
        widgets = {
            'password': PasswordInput(attrs={'class': 'form-control form-control-sm'})
        }
