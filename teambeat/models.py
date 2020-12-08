from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

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


class Organization(models.Model):
    name = models.CharField(max_length=250, unique=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True)
    admins = models.ManyToManyField(User, blank=True, null=True)

    def __str__(self):
        return '<Organization {}: "{}"" {}>'.format(
            self.pk,
            self.name,
            self.uuid
        )


class OrganizationUser(models.Model, DjangoUserMixin):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_organization_admin = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return '{}: {}'.format(self.display_name, self. organization)

    @classmethod
    def search(cls, organization, search_term):
        filter_qs = cls.objects.filter(organization=organization)
        if '@' in search_term:
            filter_qs = filter_qs.filter(user__email__icontains=search_term)
        elif ' ' in search_term:
            search_names = search_term.split(' ')
            first_name = search_names[0]
            last_name = ' '.join(search_names[1:])
            filter_qs = filter_qs.filter(
                Q(user__first_name__icontains=first_name)|
                Q(user__last_name__icontains=last_name)
            )
        else:
            filter_qs = filter_qs.filter(
                Q(user__first_name__icontains=search_term)|
                Q(user__last_name__icontains=search_term)
            )
        return filter_qs.all()



class Team(models.Model):
    name = models.CharField(max_length=250)
    organization = models.ForeignKey(
        Organization,
        null=True,
        on_delete=models.SET_NULL
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=True)
    team_lead = models.ForeignKey(
        OrganizationUser,
        related_name='teamlead_set',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = ['name', 'organization']

    def __str__(self):
        return '<Team: {} {}> // {}'.format(
            self.pk,
            self.name,
            self.organization
        )

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


class TeamMember(models.Model):
    organization_user = models.ForeignKey(
        OrganizationUser,
        on_delete=models.CASCADE
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return '<TeamMember {} {}> {}'.format(
            self.pk,
            self.user.username,
            self.team
        )

    @property
    def status_for_today(self):
        return self.teammemberstatus_set.filter(day=datetime.today()).first()

    @property
    def user(self):
        return self.organization_user.user

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

    @property
    def username(self):
        return self.user.username

    @property
    def display_name(self):
        return '{} {}'.format(self.first_name, self.last_name)





class TeamAdmin(models.Model, DjangoUserMixin):
    organization_user = models.ForeignKey(
        OrganizationUser,
        on_delete=models.CASCADE
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return '<TeamAdmin {} {}> {}'.format(
            self.pk,
            self.user.username,
            self.team.name
        )

    @property
    def user(self):
        return self.organization_user.user



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
