# Generated by Django 3.0.7 on 2021-07-29 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0004_faq'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=30, unique=True)),
                ('type', models.CharField(choices=[('Percentage', 'Percentage'), ('Fixed Price', 'Fixed Price')], max_length=30)),
                ('max_uses', models.IntegerField(null=True)),
                ('amount', models.IntegerField()),
                ('max_discount', models.IntegerField(null=True)),
                ('min_spend', models.IntegerField(null=True)),
                ('customer_limit', models.IntegerField(null=True)),
                ('active', models.BooleanField(default=True)),
                ('expiry', models.DateTimeField(null=True)),
            ],
        ),
    ]