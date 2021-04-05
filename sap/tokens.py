from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import User
import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    A unique token for a user to activate new account
    """
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp)
        )


class PasswordResetToken(PasswordResetTokenGenerator):
    """
    A unique token for a user to reset forgot password
    """
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp)
        )


account_activation_token = AccountActivationTokenGenerator()
password_reset_token = PasswordResetToken()