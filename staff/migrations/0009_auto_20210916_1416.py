# Generated by Django 3.2.5 on 2021-09-16 13:16

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0008_auto_20210914_1410'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shop_name', models.CharField(default='Test Shop', max_length=30)),
                ('primary_colour', models.CharField(default='#c1c1c1', max_length=7)),
                ('secondary_colour', models.CharField(default='#c1c1c1', max_length=7)),
                ('logo', models.BooleanField(default=False)),
                ('carousel', models.BooleanField(default=False)),
                ('maintenance', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='address',
            name='county',
            field=models.CharField(blank=True, max_length=35, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='line_2',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='code',
            field=models.UUIDField(default=uuid.UUID('7033e2a5-63d5-4a4f-a326-651145e007c6'), primary_key=True, serialize=False),
        ),
    ]
