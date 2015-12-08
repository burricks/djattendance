# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
        ('accounts', '0005_auto_20150905_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainee',
            name='services',
            field=models.ManyToManyField(to='services.Service'),
        ),
    ]
