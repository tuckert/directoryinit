# Generated by Django 3.2.2 on 2021-05-25 13:22

import directoryapp.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directoryapp', '0005_auto_20210524_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='email_sent_to',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='invitation',
            name='name_sent_to',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='invitation',
            name='number_sent_to',
            field=models.CharField(blank=True, max_length=15, null=True, validators=[directoryapp.validators.validate_us_phone_number]),
        ),
    ]
