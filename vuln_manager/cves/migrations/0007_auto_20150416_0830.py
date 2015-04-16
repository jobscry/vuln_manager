# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cves', '0006_auto_20150414_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='vulnerabilitydictionary',
            name='dictionary_file',
            field=models.FileField(upload_to='data', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vulnerabilitydictionary',
            name='etag',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vulnerabilitydictionary',
            name='last_modified',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vulnerabilitydictionary',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vulnerabilitydictionary',
            name='start',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
