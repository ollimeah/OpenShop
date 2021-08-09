# Generated by Django 3.0.7 on 2021-08-05 21:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0006_promotion_used'),
        ('storefront', '0003_auto_20210805_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='collections',
            field=models.ManyToManyField(through='storefront.BasketCollection', to='staff.Collection'),
        ),
        migrations.AlterField(
            model_name='device',
            name='code',
            field=models.UUIDField(default=uuid.UUID('577da576-9fa7-4df8-b840-2daf68c7204b'), primary_key=True, serialize=False),
        ),
    ]