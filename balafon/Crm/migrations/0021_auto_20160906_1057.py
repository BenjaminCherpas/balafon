# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0020_remove_contact_favorite_language'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='opportunity',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='display_on_board',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='entity',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='probability',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='status',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='type',
        ),
        migrations.DeleteModel(
            name='OpportunityStatus',
        ),
        migrations.DeleteModel(
            name='OpportunityType',
        ),
    ]
