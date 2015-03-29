# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cves', '0004_auto_20150329_1204'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vulnerability',
            options={'get_latest_by': 'published', 'verbose_name_plural': 'vulnerabilities'},
        ),
        migrations.RenameField(
            model_name='vulnerabilitydictionary',
            old_name='num_updates',
            new_name='num_not_updated',
        ),
        migrations.AddField(
            model_name='vulnerabilitydictionary',
            name='num_updated',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
