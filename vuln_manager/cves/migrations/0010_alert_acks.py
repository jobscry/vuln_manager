# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cves', '0009_alert'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='acks',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
