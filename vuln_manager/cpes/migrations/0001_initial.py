# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dictionary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('schema_version', models.DecimalField(max_digits=4, decimal_places=2)),
                ('product_version', models.DecimalField(max_digits=4, decimal_places=2)),
                ('generated', models.DateTimeField()),
                ('notes', models.TextField(null=True, blank=True)),
                ('num_items', models.PositiveIntegerField(default=0)),
                ('num_deprecated', models.PositiveIntegerField(default=0)),
                ('num_references', models.PositiveIntegerField(default=0)),
                ('num_existing', models.PositiveIntegerField(default=0)),
                ('start', models.FloatField(null=True, blank=True)),
                ('duration', models.FloatField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'get_latest_by': 'created',
                'verbose_name_plural': 'dictionaries',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cpe22_wfn', models.CharField(max_length=255, unique=True, null=True, blank=True)),
                ('cpe23_wfn', models.CharField(unique=True, max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('references', django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.URLField(max_length=2000), blank=True)),
                ('deprecated', models.BooleanField(default=False)),
                ('deprecation_date', models.DateTimeField(null=True, blank=True)),
                ('deprecation_type', models.CharField(default=b'NAME_CORRECTION', max_length=25, choices=[(b'NAME_CORRECTION', b'Correction'), (b'NAME_REMOVAL', b'Removal'), (b'ADDITIONAL_INFORMATION', b'Additional Information')])),
                ('deprecated_by', models.CharField(max_length=255, null=True, blank=True)),
                ('part', models.CharField(default=b'a', max_length=1, db_index=True, choices=[(b'a', b'Applications'), (b'o', b'Operating Systems'), (b'h', b'Hardware')])),
                ('vendor', models.CharField(max_length=255, db_index=True)),
                ('product', models.CharField(max_length=255, null=True, blank=True)),
                ('version', models.CharField(max_length=255, null=True, blank=True)),
                ('update', models.CharField(max_length=255, null=True, blank=True)),
                ('edition', models.CharField(max_length=255, null=True, blank=True)),
                ('language', models.CharField(max_length=255, null=True, blank=True)),
                ('sw_edition', models.CharField(max_length=255, null=True, blank=True)),
                ('target_sw', models.CharField(max_length=255, null=True, blank=True)),
                ('target_hw', models.CharField(max_length=255, null=True, blank=True)),
                ('other', models.CharField(max_length=255, null=True, blank=True)),
                ('dictionary', models.ForeignKey(to='cpes.Dictionary')),
            ],
        ),
    ]
