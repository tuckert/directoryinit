from django.contrib.auth import forms as auth_forms
from django import forms
from django.utils.translation import gettext, gettext_lazy as _


class PrettyAuthenticationForm(auth_forms.AuthenticationForm):

    username = auth_forms.UsernameField(widget=forms.TextInput(attrs={'autofocus': True,
                                                                      'class': 'form-control',
                                                                      'placeholder': 'Username'}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password',
                                          'class': 'form-control',
                                          'placeholder': 'Password'}),
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }
