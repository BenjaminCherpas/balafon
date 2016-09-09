# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0023_actiontype_show_duration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='specialcasecity',
            options={'ordering': ['departement_code', 'city'], 'verbose_name': 'special case city', 'verbose_name_plural': 'special case cities'},
        ),
        migrations.AddField(
            model_name='specialcasecity',
            name='departement_code',
            field=models.CharField(default=b'', max_length=10, verbose_name='departement code', blank=True),
        ),
        migrations.AlterField(
            model_name='specialcasecity',
            name='change_validated',
            field=models.CharField(default=b'0', max_length=3, verbose_name='change validated'),
        ),
    ]
