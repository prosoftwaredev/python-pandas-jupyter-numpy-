# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-22 08:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.SmallIntegerField(choices=[(1, 'Finance admin'), (2, 'Agency user')], help_text='Role')),
                ('user', models.OneToOneField(help_text='User', on_delete=django.db.models.deletion.CASCADE, related_name='account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Account',
                'verbose_name_plural': 'User Accounts',
            },
        ),
    ]