from django.contrib.auth.models import AbstractUser
from django.db import models


class RegularUser(AbstractUser):
    bio = models.TextField('Биография', blank=True)
