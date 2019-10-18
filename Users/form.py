from django import forms

from Users.models import User


class UserCreationForm(forms.ModelForm):
    # profile = forms.ImageField()

    name = forms.CharField(label='Full Name ', widget=forms.TextInput(attrs={'class': 'vTextField '}))
    email = forms.CharField(label="Email address", widget=forms.EmailInput(attrs={'class': 'vTextField'}))

    class Meta:
        model = User
        fields = ('name', 'email', 'mobile', 'username', 'password', 'user_type')


class FacultyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FacultyForm, self).__init__(*args, **kwargs)

        try:
            self.fields['username'].required = False
            self.fields['email'].required = True
            self.fields['name'].required = True
            # self.fields['user_type'].default = "FACULTY"
        except:
            pass
