from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model"""
    def __str__(self):
        return self.username
