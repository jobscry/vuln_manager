# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cves', '0003_auto_20150329_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_access_complexity',
            field=models.CharField(default=b'LOW', max_length=20, null=True, blank=True, choices=[(b'LOW', b'Low'), (b'MEDIUM', b'Medium'), (b'HIGH', b'High')]),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_access_vector',
            field=models.CharField(default=b'LOCAL', max_length=20, null=True, blank=True, choices=[(b'LOCAL', b'Local'), (b'ADJACENT_NETWORK', b'Adjacent Network'), (b'NETWORK', b'Network')]),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_authentication',
            field=models.CharField(default=b'NONE', max_length=20, null=True, blank=True, choices=[(b'SINGLE', b'Single'), (b'MULTIPLE', b'Multiple'), (b'NONE', b'None')]),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_availability_impact',
            field=models.CharField(default=b'NONE', max_length=20, null=True, blank=True, choices=[(b'NONE', b'None'), (b'PARTIAL', b'Partial'), (b'COMPLETE', b'Complete')]),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_base_score',
            field=models.DecimalField(null=True, max_digits=3, decimal_places=1, blank=True),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_confidentiality_impact',
            field=models.CharField(default=b'NONE', max_length=20, null=True, blank=True, choices=[(b'NONE', b'None'), (b'PARTIAL', b'Partial'), (b'COMPLETE', b'Complete')]),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_generated',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_integrity_impact',
            field=models.CharField(default=b'NONE', max_length=20, null=True, blank=True, choices=[(b'NONE', b'None'), (b'PARTIAL', b'Partial'), (b'COMPLETE', b'Complete')]),
        ),
    ]
