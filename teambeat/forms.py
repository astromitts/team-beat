from django.forms import (
    Form,
    ModelForm,
    TextInput,
    BooleanField,
    RadioSelect,
    EmailField,
    IntegerField,
    HiddenInput,
)
from teambeat.models import Team


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
    email_address = EmailField()
    class Meta:
        widgets = {
            'email_address': TextInput(attrs={'class': 'form-control'}),
        }

class RemoveTeamMemberForm(Form):
    teammember_id = IntegerField(widget=HiddenInput())
    class Meta:
        widgets = {
            'teammember_id': HiddenInput()
        }
