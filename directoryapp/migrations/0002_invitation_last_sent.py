# Generated by Django 3.2.2 on 2021-05-23 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directoryapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='last_sent',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]