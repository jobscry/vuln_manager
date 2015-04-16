# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cpes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dictionary',
            name='dictionary_file',
            field=models.FileField(upload_to='cpe_dicts', default='test'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dictionary',
            name='etag',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='dictionary',
            name='last_modified',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='deprecation_type',
            field=models.CharField(choices=[('NAME_CORRECTION', 'Correction'), ('NAME_REMOVAL', 'Removal'), ('ADDITIONAL_INFORMATION', 'Additional Information')], max_length=25, default='NAME_CORRECTION'),
        ),
        migrations.AlterField(
            model_name='item',
            name='part',
            field=models.CharField(choices=[('a', 'Applications'), ('o', 'Operating Systems'), ('h', 'Hardware')], db_index=True, max_length=1, default='a'),
        ),
    ]
