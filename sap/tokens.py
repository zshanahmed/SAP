"""
Password reset token generator module
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


"""
TODO: Nam, please verify if commenting this class is fine. We are importing a class named PasswordResetTokenGenerator
I tried commenting out this class and tried resetting the password and things work fine for me.
Please deleted the commented portion if you feel this is redundant

class PasswordResetTokenGenerator(PasswordResetTokenGenerator):
    A unique token for a user to reset forgot password
    def _make_hash_value(self, user, timestamp):
        Encrypting the token with hex value
        return (
            six.text_type(user.pk) + six.text_type(timestamp)
        )
"""


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    A unique token for a user to activate new account
    """
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp)
        )


account_activation_token = AccountActivationTokenGenerator()
password_reset_token = PasswordResetTokenGenerator()
