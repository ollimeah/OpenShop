# Generated by Django 3.2.5 on 2021-09-14 13:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0006_auto_20210913_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='email',
            field=models.EmailField(default='test@test.com', max_length=254),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='device',
            name='code',
            field=models.UUIDField(default=uuid.UUID('e5ba7786-f5c0-486a-bb07-1a3460f84d74'), primary_key=True, serialize=False),
        ),
    ]
