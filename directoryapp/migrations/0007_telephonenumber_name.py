# Generated by Django 3.2.2 on 2021-05-26 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directoryapp', '0006_auto_20210525_0822'),
    ]

    operations = [
        migrations.AddField(
            model_name='telephonenumber',
            name='name',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
