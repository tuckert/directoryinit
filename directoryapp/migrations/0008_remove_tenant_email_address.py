# Generated by Django 3.2.2 on 2021-05-26 20:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('directoryapp', '0007_telephonenumber_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tenant',
            name='email_address',
        ),
    ]