# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('cves', '0010_alert_acks'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alert',
            options={'get_latest_by': 'created'},
        ),
        migrations.AddField(
            model_name='alert',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 4, 18, 21, 9, 48, 820029, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
