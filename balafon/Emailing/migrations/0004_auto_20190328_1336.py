# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-28 13:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Emailing', '0003_auto_20180409_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailing',
            name='lang',
            field=models.CharField(blank=True, default='', max_length=5, verbose_name='language'),
        ),
    ]
