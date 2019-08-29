from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

# Create your models here.

class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    email = models.EmailField('email address', blank=True, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    username = None