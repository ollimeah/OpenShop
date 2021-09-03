# Generated by Django 3.2.5 on 2021-09-03 16:23

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('storefront', '0014_alter_device_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='code',
            field=models.UUIDField(default=uuid.UUID('47fe3b74-c3cc-4bec-b5cd-d6b27e17f4aa'), primary_key=True, serialize=False),
        ),
    ]
