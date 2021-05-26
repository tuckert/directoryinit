# Generated by Django 3.2.2 on 2021-05-14 12:09

import directoryapp.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('welcome_message', models.TextField(max_length=5000)),
                ('contact_name', models.CharField(max_length=30)),
                ('contact_email', models.EmailField(max_length=254)),
                ('contact_telephone', models.CharField(max_length=15, validators=[directoryapp.validators.validate_us_phone_number])),
                ('max_telephones_per_tenant', models.IntegerField()),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='directories', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('days_to_expire', models.IntegerField(default=3)),
                ('token', models.CharField(max_length=20)),
                ('active', models.BooleanField(default=True)),
                ('max_uses', models.IntegerField()),
                ('directory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='directoryapp.directory')),
            ],
        ),
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('email_address', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('directory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tenants', to='directoryapp.directory')),
            ],
        ),
        migrations.CreateModel(
            name='TelephoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=15, validators=[directoryapp.validators.validate_us_phone_number])),
                ('rank', models.IntegerField()),
                ('type', models.CharField(choices=[('ho', 'Home'), ('of', 'Office'), ('mo', 'Mobile'), ('ot', 'Other')], max_length=2)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='directoryapp.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='InvitationUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('fields_updated', models.JSONField()),
                ('invitation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uses', to='directoryapp.invitation')),
            ],
        ),
        migrations.AddField(
            model_name='invitation',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='directoryapp.tenant'),
        ),
    ]