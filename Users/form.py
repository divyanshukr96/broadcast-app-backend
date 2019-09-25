from django import forms

from Users.models import User


class UserCreationForm(forms.ModelForm):
    profile = forms.ImageField()

    class Meta:
        model = User
        fields = ('name', 'email', 'mobile', 'username', 'password', 'user_type', 'profile')


