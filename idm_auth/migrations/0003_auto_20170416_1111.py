# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-16 10:11
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('idm_auth', '0002_auto_20170403_2020'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='activation_code',
        ),
        migrations.AddField(
            model_name='user',
            name='date_of_birth',
            field=models.DateField(default=datetime.datetime(1970, 1, 1, 0, 0)),
            preserve_default=False,
        ),
    ]
