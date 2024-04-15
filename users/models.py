""" users.models file """
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """ custom user model """
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
