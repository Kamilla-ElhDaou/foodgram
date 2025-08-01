from django.contrib.auth.models import AbstractUser
from django.db import models

from constants import (
    MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH, MAX_FIRST_NAME_LENGTH,
    MAX_LAST_NAME_LENGTH)


class User(AbstractUser):
    """Модель для пользователя."""
    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[AbstractUser.username_validator,],
        verbose_name='Имя пользователя',
        blank=False,
        help_text='Имя пользователя',
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        verbose_name='Электронная почта',
        blank=False,
        help_text='Адрес электронной почты',
    )
    first_name = models.CharField(
        max_length=MAX_FIRST_NAME_LENGTH,
        verbose_name='Имя',
        blank=False,
        help_text='Имя',
    )
    last_name = models.CharField(
        max_length=MAX_LAST_NAME_LENGTH,
        verbose_name='Фамилия',
        blank=False,
        help_text='Фамилия',
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatars/',
        blank=True,
        null=True,
        default='frontend/src/images/avatar-icon.png',
    )
    is_subscribed = models.BooleanField(
        verbose_name='Подписка',
        default=False,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username
