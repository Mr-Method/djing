# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-02-16 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abonapp', '0008_auto_20170209_0002'),
    ]

    operations = [
        migrations.AddField(
            model_name='abontariff',
            name='deadline',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
