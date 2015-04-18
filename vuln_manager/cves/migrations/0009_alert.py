# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cpes', '0005_auto_20150418_1356'),
        ('cves', '0008_auto_20150418_1355'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('vulnerability', models.ForeignKey(to='cves.Vulnerability')),
                ('watch', models.ForeignKey(to='cpes.Watch')),
            ],
        ),
    ]
