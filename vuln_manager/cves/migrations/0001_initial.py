# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cpes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vulnerability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cve_id', models.CharField(unique=True, max_length=25)),
                ('published', models.DateTimeField()),
                ('modified', models.DateTimeField()),
                ('cwe', models.CharField(max_length=25, db_index=True)),
                ('summary', models.TextField()),
                ('references', django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.URLField(max_length=2000), blank=True)),
                ('cvss_base_score', models.DecimalField(max_digits=3, decimal_places=1)),
                ('cvss_access_vector', models.CharField(default=b'LOCAL', max_length=20, choices=[(b'LOCAL', b'Local'), (b'ADJACENT_NETWORK', b'Adjacent Network'), (b'NETWORK', b'Network')])),
                ('cvss_access_complexity', models.CharField(default=b'LOW', max_length=10, choices=[(b'LOW', b'Low'), (b'MEDIUM', b'Medium'), (b'HIGH', b'High')])),
                ('cvss_authentication', models.CharField(default=b'NONE', max_length=10, choices=[(b'SINGLE', b'Single'), (b'MULTIPLE', b'Multiple'), (b'NONE', b'None')])),
                ('cvss_confidentiality_impact', models.CharField(default=b'NONE', max_length=10, choices=[(b'NONE', b'None'), (b'PARTIAL', b'Partial'), (b'COMPLETE', b'Complete')])),
                ('cvss_integrity_impact', models.CharField(default=b'NONE', max_length=10, choices=[(b'NONE', b'None'), (b'PARTIAL', b'Partial'), (b'COMPLETE', b'Complete')])),
                ('cvss_availability_impact', models.CharField(default=b'NONE', max_length=10, choices=[(b'NONE', b'None'), (b'PARTIAL', b'Partial'), (b'COMPLETE', b'Complete')])),
                ('cvss_generated', models.DateTimeField()),
                ('cpes', models.ManyToManyField(to='cpes.Item')),
            ],
        ),
        migrations.CreateModel(
            name='VulnerabilityDictionary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num_items', models.PositiveIntegerField(default=0)),
                ('num_updates', models.PositiveIntegerField(default=0)),
                ('start', models.FloatField()),
                ('duration', models.FloatField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='vulnerability',
            name='dictionary',
            field=models.ForeignKey(to='cves.VulnerabilityDictionary'),
        ),
    ]
