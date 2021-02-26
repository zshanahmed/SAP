from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

#
# class CustomUserCreationForm(UserCreationForm):
#
#     class Meta(UserCreationForm):
#         model = get_user_model()
#         fields = ('email', 'username',) # The password field is implicitly included by default and so does not need to be explicitly named here
#
#
# class CustomUserChangeForm(UserChangeForm):
#
#     class Meta:
#         model = get_user_model()
#         fields = ('email', 'username',)









