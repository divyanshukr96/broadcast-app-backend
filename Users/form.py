from django import forms

from Users.models import User


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'email', 'mobile', 'username', 'password')

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
