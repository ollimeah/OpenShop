# Generated by Django 3.0.7 on 2021-08-14 15:01

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('storefront', '0006_auto_20210814_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='storefront.Address'),
        ),
        migrations.AlterField(
            model_name='device',
            name='code',
            field=models.UUIDField(default=uuid.UUID('a1863cb8-74ae-4bec-b5ff-5db080976b29'), primary_key=True, serialize=False),
        ),
    ]
