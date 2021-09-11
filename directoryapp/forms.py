from django import forms
from .validators import validate_us_phone_number
from .models import Directory, Invitation, TELEPHONE_TYPE_CHOICES, TelephoneNumber, Tenant
import uuid


class CreateDirectoryForm(forms.ModelForm):
    class Meta:
        model = Directory
        fields = ['name', 'welcome_message', 'contact_name', 'contact_telephone', 'contact_email',
                  'max_telephones_per_tenant']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    # owner = forms.ModelChoiceField(Directory._meta.get_field('owner').remote_field.model.objects.all())
        # widgets = {
        #     'owner': forms.ModelChoiceField(Directory._meta.get_field('owner').remote_field.model.objects.all())
        # }


class CreateInvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['expires_at', 'tenant', 'directory', 'max_uses']

    expires_at = forms.DateTimeField(widget=forms.DateTimeInput())

    def form_valid(self, form):
        if not form.instance.token:
            form.instance.token = uuid.uuid4().hex
        return super().form_valid(form)


SEND_VIA_CHOICES = [
    ('tx', 'Send via Text Message'),
    ('em', 'Send via Email'),
    ('bo', 'Send via Text Message AND Email'),
    ('no', 'Do not send')
]


class CreateInvitationFromScratchForm(forms.Form):
    directory_choices = None  # set on creation
    tenant_name = forms.CharField(max_length=30, required=False)
    # directory = forms.ModelChoiceField(queryset=None)
    tenant_number = forms.CharField(max_length=15, validators=[validate_us_phone_number], required=False)
    tenant_email = forms.EmailField(required=False)
    unlimited_uses = forms.BooleanField(initial=True, required=False)
    max_uses = forms.IntegerField(required=True, min_value=1, max_value=1000, initial=3)
    send_via = forms.ChoiceField(choices=SEND_VIA_CHOICES)


class CreateInvitationFromTenantForm(CreateInvitationFromScratchForm):
    pass


class CreateTenantFromInvitationForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = '__all__'

    directory = forms.ModelChoiceField(
        queryset=Directory.objects.all(),
        disabled=True
    )


class CreateTenantTelephoneNumberForm(forms.ModelForm):
    class Meta:
        model = TelephoneNumber
        fields = '__all__'
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        disabled=True
    )
