# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-27 10:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0007_auto_20170727_0004'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportrelease',
            name='period',
            field=models.OneToOneField(help_text='Report period', null=True, on_delete=django.db.models.deletion.CASCADE, to='report.ReportPeriod'),
        ),
    ]