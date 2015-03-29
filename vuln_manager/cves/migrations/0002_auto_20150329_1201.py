# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cves', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vulnerability',
            options={'verbose_name_plural': 'vulnerabilities'},
        ),
        migrations.AlterModelOptions(
            name='vulnerabilitydictionary',
            options={'verbose_name_plural': 'Vulnerability Dictionaries'},
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_access_complexity',
            field=models.CharField(default=b'LOW', max_length=20, choices=[(b'LOW', b'Low'), (b'MEDIUM', b'Medium'), (b'HIGH', b'High')]),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_authentication',
            field=models.CharField(default=b'NONE', max_length=20, choices=[(b'SINGLE', b'Single'), (b'MULTIPLE', b'Multiple'), (b'NONE', b'None')]),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_availability_impact',
            field=models.CharField(default=b'NONE', max_length=20, choices=[(b'NONE', b'None'), (b'PARTIAL', b'Partial'), (b'COMPLETE', b'Complete')]),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_confidentiality_impact',
            field=models.CharField(default=b'NONE', max_length=20, choices=[(b'NONE', b'None'), (b'PARTIAL', b'Partial'), (b'COMPLETE', b'Complete')]),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_integrity_impact',
            field=models.CharField(default=b'NONE', max_length=20, choices=[(b'NONE', b'None'), (b'PARTIAL', b'Partial'), (b'COMPLETE', b'Complete')]),
        ),
    ]
