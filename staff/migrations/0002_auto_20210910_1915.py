# Generated by Django 3.2.5 on 2021-09-10 18:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='device',
            name='code',
            field=models.UUIDField(default=uuid.UUID('902d85a1-4351-4507-9717-a5271ab3f286'), primary_key=True, serialize=False),
        ),
    ]
