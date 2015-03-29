# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cves', '0002_auto_20150329_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vulnerability',
            name='cwe',
            field=models.CharField(db_index=True, max_length=25, null=True, blank=True),
        ),
    ]
