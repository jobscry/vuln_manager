# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cves', '0007_auto_20150416_0830'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vulnerabilitydictionary',
            options={'get_latest_by': 'created', 'verbose_name_plural': 'Vulnerability Dictionaries'},
        ),
    ]
