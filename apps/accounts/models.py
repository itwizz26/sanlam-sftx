from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    @property
    def is_member(self):
        return not self.is_staff