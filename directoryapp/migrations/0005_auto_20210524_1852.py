# Generated by Django 3.2.2 on 2021-05-24 23:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('directoryapp', '0004_invitation_link'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telephonenumber',
            name='rank',
        ),
        migrations.AlterField(
            model_name='telephonenumber',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='numbers', to='directoryapp.tenant'),
        ),
    ]