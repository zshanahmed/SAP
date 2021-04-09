"""
Password reset token generator module
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class AccountActivationToken(PasswordResetTokenGenerator):
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


account_activation_token = AccountActivationToken()
password_reset_token = PasswordResetToken()
