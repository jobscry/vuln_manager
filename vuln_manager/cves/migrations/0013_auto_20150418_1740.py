# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cves', '0012_vulnerabilitydictionary_processed_alerts'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='alert',
            unique_together=set([('vulnerability', 'watch')]),
        ),
    ]
