# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cpes', '0004_alert'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Alert',
            new_name='Watch',
        ),
    ]
