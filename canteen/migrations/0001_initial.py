# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Canteen',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=50, null=True)),
                ('phone_number', models.CharField(max_length=12, null=True)),
                ('manager', models.ForeignKey(related_name='manager', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('delivery', models.BooleanField(default=True)),
                ('customer_phoneNum', models.CharField(max_length=15)),
                ('restaurant_phoneNum', models.CharField(max_length=15, null=True)),
                ('order', models.CharField(default=b'[]', max_length=200)),
                ('total_money', models.FloatField(default=0.0)),
                ('name_address', models.CharField(max_length=50, null=True)),
                ('last_message', models.CharField(max_length=30, null=True)),
                ('restaurant', models.ForeignKey(to='canteen.Canteen', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('num', models.IntegerField(null=True)),
                ('dish_type', models.CharField(default=b'food', max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('price', models.FloatField(null=True)),
                ('description', models.CharField(max_length=100, null=b'Add description for this dish')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('info', models.CharField(max_length=200, null=True)),
                ('last_updated', models.DateTimeField(auto_now_add=True)),
                ('dishtype_list', models.CharField(default=b'["food","drinks"]', max_length=200)),
                ('restaurant', models.ForeignKey(to='canteen.Canteen', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='dish',
            name='menu',
            field=models.ForeignKey(to='canteen.Menu', null=True),
        ),
        migrations.AddField(
            model_name='dish',
            name='restaurant',
            field=models.ForeignKey(to='canteen.Canteen', null=True),
        ),
    ]
