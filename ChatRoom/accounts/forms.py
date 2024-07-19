from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Имя")

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "password1",
            "password2",
        )