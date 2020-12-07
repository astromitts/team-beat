from django.db import models
from django.contrib.auth.models import User

from datetime import datetime
import uuid


class DjangoUserMixin(object):
    @property
    def username(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def display_name(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Team(models.Model):
    name = models.CharField(max_length=250, unique=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True)
    team_lead = models.ForeignKey(
        User,
        related_name='teamlead_set',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return '<Team: {} {}>'.format(self.pk, self.name)

    def teamstatus_set(self, day=None):
        if not day:
            day = datetime.today()
        return TeamMemberStatus.objects.filter(teammember__team=self)

    def teamstatus(self, day=None):
        if not day:
            day = datetime.today()
        has_red = False
        has_yellow = False
        has_green = False
        for status in self.teamstatus_set(day):
            if status.status == 'red':
                has_red = True
            elif status.status == 'yellow':
                has_yellow = True
            elif status.status == 'green':
                has_green = True
        if has_red:
            return 'red'
        if has_yellow:
            return 'yellow'
        if has_green:
            return 'green'
        return None


class TeamMember(models.Model, DjangoUserMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return '<TeamMember {} {}> {}'.format(self.pk, self.user.username, self.team)

    @property
    def status_for_today(self):
        return self.teammemberstatus_set.filter(day=datetime.today()).first()



class TeamAdmin(models.Model, DjangoUserMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return '<TeamAdmin {} {}> {}'.format(self.pk, self.user.username, self.team.name)



class TeamMemberStatus(models.Model):
    teammember = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    day = models.DateField(default=datetime.today)
    status = models.CharField(
        max_length=10,
        choices=(
            ('green', 'green'),
            ('red', 'red'),
            ('yellow', 'yellow'),
        )
    )
    additional_info_for_team = models.TextField(blank=True, null=True)
    additional_info_for_lead = models.TextField(blank=True, null=True)

    def __str__(self):
        return '<TeamMemberStatus {} {} {}>'.format(
            self.teammember.team.name,
            self.teammember.user.username,
            self.day
        )
