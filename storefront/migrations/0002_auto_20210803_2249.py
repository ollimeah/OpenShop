# Generated by Django 3.0.7 on 2021-08-03 21:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storefront', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='basket',
            old_name='device',
            new_name='device_id',
        ),
        migrations.RenameField(
            model_name='device',
            old_name='device',
            new_name='device_id',
        ),
    ]
