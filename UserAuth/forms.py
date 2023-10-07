from django import forms
from . import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    class Meta:
        model = models.User
        fields = ('username', 'password')

class RegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}), max_length=64, required=False)
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password Again'}))
    tier = forms.ModelChoiceField(queryset=models.UserTier.objects.all(), required=False)

    class Meta(UserCreationForm.Meta):
        model = models.User
        fields = UserCreationForm.Meta.fields + ('email', 'tier')