# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0021_auto_20160906_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='archived',
            field=models.BooleanField(default=False, verbose_name='archived'),
        ),
    ]
