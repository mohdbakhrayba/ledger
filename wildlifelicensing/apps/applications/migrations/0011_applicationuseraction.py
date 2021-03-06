# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-10-12 02:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wl_applications', '0010_auto_20160901_1436'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationUserAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('what', models.TextField()),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wl_applications.Application')),
                ('who', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
