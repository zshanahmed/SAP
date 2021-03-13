from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model


# User = get_user_model()


class UpdateAdminProfileForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email'
        ]


class UserPasswordForgotForm(PasswordResetForm):
    """
    Forgot password: user enter registered email address to reset password
    """
    email = forms.EmailField(label='Email address',
                             max_length=254,
                             required=True,
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control',
                                        'placeholder': 'Email address...',
                                        'type': 'text',
                                        'id': 'email_address'
                                        }
                             ))


class UserResetForgotPasswordForm(SetPasswordForm):
    """
    Form to set new password, in case user forgets old passwords
    """
    new_password1 = forms.CharField(label='Password',
                                    help_text="<ul class='errorlist text-muted'><li>Your password can 't be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can 't be a commonly used password.</li> <li>Your password can 't be entirely numeric.<li></ul>",
                                    max_length=100,
                                    required=True,
                                    widget=forms.PasswordInput(
                                        attrs={
                                            'class': 'form-control',
                                            'placeholder': 'New password...',
                                            'type': 'password',
                                            'id': 'user_password',
                                        }))

    new_password2 = forms.CharField(label='Confirm password',
                                    help_text=False,
                                    max_length=100,
                                    required=True,
                                    widget=forms.PasswordInput(
                                        attrs={
                                            'class': 'form-control',
                                            'placeholder': 'Repeat new password...',
                                            'type': 'password',
                                            'id': 'user_password',
                                        }))
