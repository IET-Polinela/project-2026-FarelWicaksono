from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CitizenRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_admin = False  # Otomatis mendaftar sebagai Citizen biasa (Poin 3)
        user.is_member = True
        if commit:
            user.save()
        return user