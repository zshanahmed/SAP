from django.contrib.auth.models import User
from django.forms import ModelForm

class UpdateAdminProfileForm(ModelForm):

    class Meta:
        model = User
        fields = [
            'username',
            'email'
        ]
