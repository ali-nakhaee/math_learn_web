""" users.models file """
from django.db import models
from django.contrib.auth.models import AbstractUser, Group


class User(AbstractUser):
    """ custom user model """
    TEACHER = 'TEACHER'
    STUDENT = 'STUDENT'

    ROLE_CHOICES = (
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
    )

    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=STUDENT)
    students = models.ManyToManyField('self', symmetrical=False, related_name='teachers', blank=True)
    key = models.CharField(max_length=8, null=True, blank=True)

    def save(self, *args, **kwargs):
            super().save(*args, **kwargs)
            if self.role == self.TEACHER:
                group, created = Group.objects.get_or_create(name='teachers')
                group.user_set.add(self)
            elif self.role == self.STUDENT:
                group, created = Group.objects.get_or_create(name='students')
                group.user_set.add(self)