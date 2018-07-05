# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-04-09 13:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Emailing', '0002_auto_20160601_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailing',
            name='from_email',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='From email'),
        ),
        migrations.AlterField(
            model_name='emailing',
            name='lang',
            field=models.CharField(blank=True, choices=[('', 'Default'), ('en', 'English'), ('fr', 'Français')], default='', max_length=5, verbose_name='language'),
        ),
        migrations.AlterField(
            model_name='magiclink',
            name='uuid',
            field=models.CharField(blank=True, db_index=True, default='', max_length=100),
        ),
    ]