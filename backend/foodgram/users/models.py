from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    """
    Модель пользователя.
    """

    email = models.EmailField(
        verbose_name='Электронная почта',
        help_text='Введите вашу электронную почту',
        max_length=settings.LIMIT_USER_EMAIL_LENGTH,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        help_text='Придумайте юзернейм',    
        max_length=settings.LIMIT_USERNAME_LENGTH,
        null=False,
        unique=True,
        db_index=True,
        validators=[
            UnicodeUsernameValidator(),
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        help_text='Введите ваше имя',
        max_length=settings.LIMIT_FIRST_NAME_LENGTH,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        help_text='Введите вашу фамилию',
        max_length=settings.LIMIT_LAST_NAME_LENGTH,
    )
    password = models.CharField(
        verbose_name='Пароль',
        help_text='Введите пароль',
        max_length=settings.LIMIT_PASSWORD_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', )

    def __str__(self) -> str:
        """
        Строковое представление пользователя.
        """
        return f'{self.username} ({self.first_name} {self.last_name})'
    

    def __repr__(self) -> str:
        """
        Формальное строковое преставление пользователя.
        """
        return (
            f'{self.__class__.__name__}(username="{self.username}", '
            f'last_name="{self.last_name}", first_name="{self.first_name}", '
            f'email="{self.email}", password="{self.password}")'
        )