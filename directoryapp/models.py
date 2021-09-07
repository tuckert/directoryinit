from django.db import models
from django.contrib.auth import get_user_model
from .utils import unique_slug_generator
from django.db.models.signals import pre_save, post_save
from .validators import validate_us_phone_number
import phonenumbers

User = get_user_model()


# Create your models here.
class Directory(models.Model):
    name = models.CharField(max_length=50, null=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='directories')
    welcome_message = models.TextField(max_length=5000, null=False)
    contact_name = models.CharField(max_length=30, null=False)
    contact_email = models.EmailField(null=False)
    contact_telephone = models.CharField(max_length=15, validators=[validate_us_phone_number])
    max_telephones_per_tenant = models.IntegerField()
    slug = models.SlugField(unique=True, blank=True)

    @property
    def title(self):
        return self.name

    def get_absolute_url(self):
        return '/d/' + self.slug

    def __str__(self):
        return self.name

    def unused_invitations(self):
        print('wtf')
        unused = self.invitations.filter(tenant=None).count()
        return str(unused) + ' unused links sent.'


def system_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


# runs unique slug generator before the object is saved
pre_save.connect(system_pre_save_receiver, sender=Directory)


class Tenant(models.Model):
    name = models.CharField(max_length=30)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE, null=False, related_name='tenants')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + ' @ ' + str(self.directory)

    def get_absolute_url(self):
        return '/d/' + self.directory.slug + '/tenant/' + str(self.pk)

    def invites_and_uses(self):
        invites = self.invitations.count()
        uses = InvitationUsage.objects.filter(invitation__in=self.invitations.all()).count()
        return str(invites) + ' invitations sent; used ' + str(uses) + ' times.'


TELEPHONE_TYPE_CHOICES = [
    ('ho', 'Home'),
    ('of', 'Office'),
    ('mo', 'Mobile'),
    ('ot', 'Other'),
]


class TelephoneNumber(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=False, blank=False, related_name='numbers')
    number = models.CharField(max_length=15, validators=[validate_us_phone_number])
    type = models.CharField(max_length=2, choices=TELEPHONE_TYPE_CHOICES)
    name = models.CharField(max_length=20, blank=True, null=True)

    @property
    def real_number(self):
        number = phonenumbers.parse(self.number, 'US')
        return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)

    def __str__(self):
        return 'Number for ' + str(self.tenant) + ': ' + self.number


class Invitation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent = models.DateTimeField(blank=True, null=True)
    days_to_expire = models.IntegerField(null=False, default=3)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='invitations', blank=True, null=True)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE, null=False, related_name='invitations')
    active = models.BooleanField(default=True)
    private_use = models.BooleanField(default=False)
    max_uses = models.IntegerField()
    link = models.CharField(max_length=120, blank=True, null=True)
    name_sent_to = models.CharField(max_length=15, blank=True, null=True)
    number_sent_to = models.CharField(max_length=15, validators=[validate_us_phone_number], blank=True, null=True)
    email_sent_to = models.EmailField(blank=True, null=True)

    def __str__(self):
        return 'Invitation for ' + str(self.tenant)

    @property
    def active_status(self):
        if self.active:
            return 'Invitation link is active'
        else:
            return 'Invitation link has been deativated'


class InvitationUsage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE, related_name='uses')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='invitation_uses')
    ip_address = models.GenericIPAddressField()
    fields_updated = models.JSONField()

    def __str__(self):
        return 'Usage for ' + str(self.invitation) + 'at ' + str(self.created_at)


# If the amount of usages is GTE to the set max_uses on the invitation, de-activate the invitation and link.
def invitation_usage_pre_save_receiver(sender, instance, *args, **kwargs):
    if instance.invitation.uses.count() >= instance.invitation.max_uses\
            and instance.invitation.max_uses is not 0:
        instance.invitation.active = False
        instance.invitation.save()


# connect to Invitation Presave
post_save.connect(invitation_usage_pre_save_receiver, sender=InvitationUsage)
