# Generated by Django 3.1.3 on 2020-12-09 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session_manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to_email', models.EmailField(max_length=254)),
                ('from_email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=300)),
                ('body', models.TextField()),
            ],
        ),
    ]
