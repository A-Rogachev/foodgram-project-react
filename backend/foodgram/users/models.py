from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator
from django.db import models

from users.validators import validate_username_not_me, validate_name


class User(AbstractUser):
    """
    Модель пользователя.
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    email = models.EmailField(
        verbose_name='Электронная почта',
        help_text='Введите вашу электронную почту',
        max_length=settings.LIMIT_USER_EMAIL_LENGTH,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        help_text='Придумайте имя профиля',
        max_length=settings.LIMIT_USER_NAMES_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            validate_username_not_me,
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        help_text='Введите ваше имя',
        max_length=settings.LIMIT_USER_NAMES_LENGTH,
        validators=[
            validate_name,
        ]
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        help_text='Введите вашу фамилию',
        max_length=settings.LIMIT_USER_NAMES_LENGTH,
        validators=[
            validate_name,
        ]
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', )

    def save(self, *args, **kwargs):
        """
        Сохраняет имя и фамилию пользователя в корректном регистре.
        """
        self.first_name = self.first_name.capitalize()
        self.last_name = self.last_name.capitalize()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Строковое представление пользователя.
        """
        return f'{self.username}'


class Subscription(models.Model):
    """
    Модель подписки.
    """

    subscriber = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='subscriber',
        on_delete=models.CASCADE,
    )

    publisher = models.ForeignKey(
        User,
        verbose_name='Автор контента',
        related_name='publisher',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('publisher', )
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'publisher'],
                name='unique follow'
            ),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(subscriber=models.F('publisher')),
            ),
        ]

    def __str__(self) -> str:
        """
        Строковое представление подписки.
        """
        return f'{self.subscriber} подписан на {self.publisher}'
