# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cpes', '0002_auto_20150414_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dictionary',
            name='dictionary_file',
            field=models.FileField(upload_to='data'),
        ),
    ]
