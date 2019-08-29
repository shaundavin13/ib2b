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
    level = models.IntegerField()

    def get_subordinates(self):
        return getattr(self, f'subordinates_{self.level}')

    level_2_superior = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='subordinates_2', null=True)
    level_3_superior = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='subordinates_3', null=True)
    level_4_superior = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='subordinates_4', null=True)
    level_5_superior = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='subordinates_5', null=True)
    level_6_superior = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='subordinates_6', null=True)
