from django.contrib.auth.models import AbstractUser
from django.db import models
from users.validators import validate_username

from .constants import MAX_EMAIL_LENGTH, MAX_STRING_LENGTH


class RegularUser(AbstractUser):
    username = models.CharField(
        verbose_name='Логин',
        max_length=MAX_STRING_LENGTH,
        unique=True,
        validators=[validate_username],
    )
    avatar = models.ImageField(
        upload_to='users/images/',
        null=True,
        default=None
    )
    email = models.EmailField(
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
    )

    def __str__(self):
        return self.username
