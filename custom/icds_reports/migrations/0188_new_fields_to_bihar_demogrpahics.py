# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-05-10 08:23
from __future__ import unicode_literals

from django.db import migrations, models

from custom.icds_reports.utils.migrations import get_view_migrations


class Migration(migrations.Migration):

    dependencies = [
        ('icds_reports', '0187_chm_view_growth_tracker'),
    ]

    operations = [
        migrations.AddField(
            model_name='biharapidemographics',
            name='age_marriage',
            field=models.SmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='biharapidemographics',
            name='last_referral_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='biharapidemographics',
            name='migrate_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='biharapidemographics',
            name='referral_health_problem',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='biharapidemographics',
            name='referral_reached_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='biharapidemographics',
            name='referral_reached_facility',
            field=models.SmallIntegerField(null=True),
        ),
    ]

    operations.extend(get_view_migrations())
