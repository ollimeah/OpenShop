# Generated by Django 3.2.5 on 2021-09-03 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0012_remove_ordercollectionproduct_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordershipping',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='staff.order'),
        ),
    ]