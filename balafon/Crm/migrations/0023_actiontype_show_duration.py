# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0022_entity_archived'),
    ]

    operations = [
        migrations.AddField(
            model_name='actiontype',
            name='show_duration',
            field=models.BooleanField(default=False, help_text='show duration rather than end date on actions', verbose_name='show duration'),
        ),
    ]
