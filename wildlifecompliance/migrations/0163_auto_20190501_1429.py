# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-05-01 06:29
from __future__ import unicode_literals

from django.db import migrations, models
import wildlifecompliance.components.returns.models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0162_merge_20190430_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='returntype',
            name='data_template',
            field=models.FileField(blank=True, null=True, upload_to=wildlifecompliance.components.returns.models.template_directory_path),
        ),
    ]