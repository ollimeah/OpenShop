# Generated by Django 3.2.5 on 2021-08-04 19:51

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('staff', '0006_promotion_used'),
        ('storefront', '0002_auto_20210804_2051'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('code', models.CharField(default=uuid.UUID('d35d8064-586b-42d2-82ce-c57d504b736a'), max_length=40, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('collections', models.ManyToManyField(to='staff.Collection')),
                ('device_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='storefront.device')),
                ('products', models.ManyToManyField(to='staff.Product')),
            ],
        ),
    ]
