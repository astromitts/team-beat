# Generated by Django 3.1.3 on 2020-12-09 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session_manager', '0002_emaillog'),
    ]

    operations = [
        migrations.AddField(
            model_name='emaillog',
            name='email_type',
            field=models.CharField(default='app invitation', max_length=50),
            preserve_default=False,
        ),
    ]