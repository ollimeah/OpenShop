# Generated by Django 3.2.5 on 2021-09-03 16:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0011_auto_20210903_1527'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordercollectionproduct',
            name='quantity',
        ),
    ]