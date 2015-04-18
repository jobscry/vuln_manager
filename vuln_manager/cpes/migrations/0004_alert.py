# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cpes', '0003_auto_20150416_0830'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('vendor', models.CharField(max_length=255, db_index=True)),
                ('product', models.CharField(max_length=255, db_index=True)),
                ('version', models.CharField(max_length=255, db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
