# Generated by Django 3.2.5 on 2021-08-04 21:20

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('staff', '0006_promotion_used'),
    ]

    operations = [
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('collections', models.ManyToManyField(to='staff.Collection')),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('code', models.UUIDField(default=uuid.UUID('db7849bc-957f-421c-b084-4c04705a5a65'), primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='BasketProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('basket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='storefront.basket')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.product')),
            ],
        ),
        migrations.AddField(
            model_name='basket',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='storefront.device'),
        ),
        migrations.AddField(
            model_name='basket',
            name='products',
            field=models.ManyToManyField(through='storefront.BasketProduct', to='staff.Product'),
        ),
    ]