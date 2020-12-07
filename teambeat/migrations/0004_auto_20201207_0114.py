# Generated by Django 3.1.3 on 2020-12-07 01:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teambeat', '0003_teamadmin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='team_lead',
        ),
        migrations.AddField(
            model_name='team',
            name='team_lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='TeamLead',
        ),
    ]
