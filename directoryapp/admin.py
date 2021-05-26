from django.contrib import admin
from directoryapp.models import Directory, Tenant, TelephoneNumber, Invitation, InvitationUsage


# Register your models here.
admin.site.register([Directory, Tenant, TelephoneNumber, Invitation, InvitationUsage])
