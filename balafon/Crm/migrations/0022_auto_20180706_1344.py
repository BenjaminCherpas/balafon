# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-06 13:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0021_auto_20180406_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='actiontype',
            name='label',
            field=models.CharField(blank=True, default='', help_text='If set, replace name on commercial document', max_length=100, verbose_name='label'),
        )
    ]
