from django import forms
from django.utils.translation import gettext_lazy as _

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label=_("نام کاربری"),)
    password = forms.CharField(max_length=150, widget=forms.PasswordInput, label=_("رمز عبور"))
