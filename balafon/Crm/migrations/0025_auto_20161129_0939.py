# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0024_auto_20160909_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='export_to',
            field=models.CharField(default='', max_length=50, blank=True, help_text='Name of the column when exporting contact to Excel. If empty, not exported. Two groups can have the same column and will be separated by commas', verbose_name='Export to', db_index=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='district_id',
            field=models.CharField(max_length=10, null=True, verbose_name='district id', blank=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='latitude',
            field=models.FloatField(null=True, verbose_name='latitude', blank=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='longitude',
            field=models.FloatField(null=True, verbose_name='longitude', blank=True),
        ),
    ]
