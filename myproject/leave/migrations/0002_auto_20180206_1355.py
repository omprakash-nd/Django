# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-06 13:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='code',
            field=models.IntegerField(unique=True),
        ),
    ]