# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cpes', '0005_auto_20150418_1356'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='watch',
            options={'verbose_name_plural': 'watches'},
        ),
        migrations.AddField(
            model_name='watch',
            name='part',
            field=models.CharField(max_length=1, default='a', db_index=True, choices=[('a', 'Applications'), ('o', 'Operating Systems'), ('h', 'Hardware')]),
        ),
    ]
