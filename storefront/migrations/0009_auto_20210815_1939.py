# Generated by Django 3.0.7 on 2021-08-15 18:39

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('storefront', '0008_auto_20210815_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='code',
            field=models.UUIDField(default=uuid.UUID('a7125e51-a112-4f94-8bf2-68373dbd99af'), primary_key=True, serialize=False),
        ),
    ]