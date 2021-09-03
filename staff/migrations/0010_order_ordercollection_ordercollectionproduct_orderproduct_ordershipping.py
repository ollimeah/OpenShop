# Generated by Django 3.2.5 on 2021-09-03 14:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0009_address_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('promotion_code', models.CharField(max_length=30, unique=True)),
                ('discount_amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('date_ordered', models.DateTimeField(auto_now=True)),
                ('shipped', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='OrderCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection_name', models.CharField(max_length=255)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderShipping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_name', models.CharField(max_length=127)),
                ('line_1', models.CharField(max_length=255)),
                ('line_2', models.CharField(max_length=255, null=True)),
                ('city', models.CharField(max_length=35)),
                ('county', models.CharField(max_length=35, null=True)),
                ('postcode', models.CharField(max_length=8)),
                ('delivery_name', models.CharField(max_length=255)),
                ('delivery_price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=255)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderCollectionProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=255)),
                ('quantity', models.IntegerField()),
                ('order_collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.ordercollection')),
            ],
        ),
    ]