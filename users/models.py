from django.db import models
from django.contrib.auth.models import AbstractUser
import os

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    ACCESS_LEVEL_CHOICES = (
        ('admin', 'System Managers'),
        ('superadmin', 'Data Manager Officers'),
    )

    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username

    def get_human_readable_access_level(self):
        for choice in self.ACCESS_LEVEL_CHOICES:
            if choice[0] == self.access_level:
                return choice[1]

        return 'Unknown'
