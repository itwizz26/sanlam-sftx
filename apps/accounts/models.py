from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Meta:
        swappable = 'AUTH_USER_MODEL'
    @property
    def is_member(self):
        return not self.is_staff