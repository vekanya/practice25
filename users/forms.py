from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # ← ОДИН пароль!
        if commit:
            user.save()
        return user  # ← возвращаем!

class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('avatar',)
