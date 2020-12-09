from django.forms import (
    BooleanField,
    CharField,
    EmailField,
    EmailInput,
    Form,
    HiddenInput,
    IntegerField,
    ModelForm,
    RadioSelect,
    Select,
    TextInput,
)
from django.core.exceptions import ValidationError

from teambeat.models import Team, Organization


class CreateOrganizationForm(Form):
    organization_name = CharField(widget=TextInput(attrs={'class': 'form-control'}))

    def clean(self):
        super(CreateOrganizationForm, self).clean()
        data = self.cleaned_data
        if Organization.objects.filter(name=data['organization_name']):
            raise ValidationError('An organization with this name already exists')


class TeamForm(ModelForm):
    creator_is_member = BooleanField(
        widget=RadioSelect(choices=(('Y', 'Yes'), ('N', 'No')), attrs={'class': 'choices-inline'}),
        label='Are you a member of this team?',
        help_text='This means you will be asked to give your daily status along with other teammembers'
    )
    creator_is_lead = BooleanField(
        widget=RadioSelect(choices=(('Y', 'Yes'), ('N', 'No')), attrs={'class': 'choices-inline'}),
        label='Are you the Team Lead of this team?',
        help_text='This means you will be given daily status updates from teammembers'

    )
    class Meta:
        model = Team
        fields = ['name', 'creator_is_member', 'creator_is_lead']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
        }


class SearchUsersForm(Form):
    search_term = CharField(label='name or email')
    class Meta:
        widgets = {
            'search_term': TextInput(attrs={'class': 'form-control'}),
        }


class RemoveTeamMemberForm(Form):
    teammember_id = IntegerField(widget=HiddenInput())
    class Meta:
        widgets = {
            'teammember_id': HiddenInput()
        }


class SetOrganizationForm():
    organization = CharField(
        widget=Select(
            choices=[],
            attrs={'class': 'form-control'}
        )
    )

    class Meta:
        fields = ['organization']

    def __init__(self, user, *args, **kwargs):
        super(SetOrganizationForm, self).__init__(*args, **kwargs)
        user_orgs = user.organization_set.all()
        organization_choices = [[uo.pk, uo.name] for uo in user_orgs]
        self.organization.widget.choice = organization_choices


class InviteUserForm(Form):
    email = EmailField(widget=EmailInput(attrs={'class': 'form-control'}))
