from django.contrib.auth.models import AbstractUser
from django.db import models

from constants import (MAX_EMAIL_LENGTH, MAX_FIRST_NAME_LENGTH,
                       MAX_LAST_NAME_LENGTH, MAX_USERNAME_LENGTH)


class User(AbstractUser):
    """Модель для пользователя с расширенными полями профиля.

    Атрибуты:
        avatar (ImageField): Аватар пользователя (опционально).
    """

    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[AbstractUser.username_validator, ],
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        max_length=MAX_FIRST_NAME_LENGTH,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=MAX_LAST_NAME_LENGTH,
        verbose_name='Фамилия',
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatars/',
        blank=True,
        default='frontend/src/images/avatar-icon.png',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username', 'first_name', 'last_name', 'password',
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        """Строковое представление объекта."""
        return self.username
