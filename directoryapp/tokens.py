from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int


# Using Django's PasswordResetTokenGenerator as an "invitation" maker.  Working exactly as a password-reset
# link to verify private links sent in an e-mail.
class InvitationTokenGenerator(PasswordResetTokenGenerator):

    # By default, this module uses the User.  Change up here so that it uses an "Invitation"
    def _make_hash_value(self, invitation, timestamp):
        return (
            invitation.pk + timestamp +
            invitation.active
        )

    # By default, this checks against PASSWORD_RESET_TIMEOUT (3 days default).  Any older link gets booted.
    # We want links to last as long as they're programmed to (based on the Invitation.days_to_expire).
    def check_token(self, user, token):

        #  Everything below this is from Django
        ########################################
        """
        Check that a password reset token is correct for a given user.
        """
        if not (user and token):
            return False
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
            # RemovedInDjango40Warning.
            legacy_token = len(ts_b36) < 4
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            # RemovedInDjango40Warning: when the deprecation ends, replace
            # with:
            #   return False
            if not constant_time_compare(
                self._make_token_with_timestamp(user, ts, legacy=True),
                token,
            ):
                return False

        # RemovedInDjango40Warning: convert days to seconds and round to
        # midnight (server time) for pre-Django 3.1 tokens.
        now = self._now()

        ###################################################
        #   Everything above this is taken from Django

        # Check the timestamp is within limit.

        # 'user' is actually Invitation.  Here we check the timestamp against the expiration set by the invitation.
        if (self._num_seconds(now) - ts) > user.days_to_expire_in_seconds:
            return False

        return True


account_activation_token = InvitationTokenGenerator()
