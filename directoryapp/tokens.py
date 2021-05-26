from django.contrib.auth.tokens import PasswordResetTokenGenerator


class InvitationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, invitation, timestamp):
        return (
            invitation.pk + timestamp +
            invitation.active
        )


account_activation_token = InvitationTokenGenerator()
