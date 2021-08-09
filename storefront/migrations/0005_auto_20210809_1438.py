# Generated by Django 3.0.7 on 2021-08-09 13:38

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0006_promotion_used'),
        ('storefront', '0004_auto_20210805_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='promotion',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.Promotion'),
        ),
        migrations.AlterField(
            model_name='device',
            name='code',
            field=models.UUIDField(default=uuid.UUID('e16e0a2f-03c9-42a2-9399-31285a9f9628'), primary_key=True, serialize=False),
        ),
    ]