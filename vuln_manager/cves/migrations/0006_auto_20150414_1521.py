# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cves', '0005_auto_20150329_1245'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vulnerability',
            options={'verbose_name_plural': 'vulnerabilities', 'get_latest_by': 'modified', 'ordering': ['-published', '-modified']},
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_access_complexity',
            field=models.CharField(null=True, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')], max_length=20, blank=True, default='LOW'),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_access_vector',
            field=models.CharField(null=True, choices=[('LOCAL', 'Local'), ('ADJACENT_NETWORK', 'Adjacent Network'), ('NETWORK', 'Network')], max_length=20, blank=True, default='LOCAL'),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_authentication',
            field=models.CharField(null=True, choices=[('SINGLE', 'Single'), ('MULTIPLE', 'Multiple'), ('NONE', 'None')], max_length=20, blank=True, default='NONE'),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_availability_impact',
            field=models.CharField(null=True, choices=[('NONE', 'None'), ('PARTIAL', 'Partial'), ('COMPLETE', 'Complete')], max_length=20, blank=True, default='NONE'),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_confidentiality_impact',
            field=models.CharField(null=True, choices=[('NONE', 'None'), ('PARTIAL', 'Partial'), ('COMPLETE', 'Complete')], max_length=20, blank=True, default='NONE'),
        ),
        migrations.AlterField(
            model_name='vulnerability',
            name='cvss_integrity_impact',
            field=models.CharField(null=True, choices=[('NONE', 'None'), ('PARTIAL', 'Partial'), ('COMPLETE', 'Complete')], max_length=20, blank=True, default='NONE'),
        ),
    ]
