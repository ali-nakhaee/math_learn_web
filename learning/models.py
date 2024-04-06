""" learning.models file """
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Practice(models.Model):
    """ Base model for each learning course """
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)



class ConstantText(models.Model):
    """ Constant texts for each practice """
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    text = models.TextField()
    step = models.PositiveIntegerField()
