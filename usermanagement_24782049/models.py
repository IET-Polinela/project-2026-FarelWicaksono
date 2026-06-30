from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)  # Sesuai poin 1 modul
    is_member = models.BooleanField(default=True)  # Sesuai poin 1 modul

    def __str__(self):
        return self.username