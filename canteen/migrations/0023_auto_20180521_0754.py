# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canteen', '0022_auto_20180511_0106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='dishtype_list',
            field=models.CharField(default=b'["food","drinks"]', max_length=200),
        ),
    ]
