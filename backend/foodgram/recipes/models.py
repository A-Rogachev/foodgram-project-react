from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model


User = get_user_model()

class Tag(models.Model):
    """
    Метка для фильтрации рецептов.
    """

    name = models.CharField(
        verbose_name='Название',
        help_text='Введите название тега',
        max_length=200,
    )
    color = models.CharField(
        verbose_name='Цвет виджета тега',
        help_text='Введите текст для тега',
        max_length=7,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^#[A-Z0-9_]{6}$',
                message=(
                    'Обозначение цвета должно состоять из знака # '
                    ' и 6 символов (заглавные буквы/цифры) после!'
                ),
            ),
        ]
    )
    slug = models.CharField(
        verbose_name='Слаг тега',
        help_text='Введите слаг для тега',
        unique=True,
        max_length=200,
        validators=[
            RegexValidator(
                regex= r'^[-a-zA-Z0-9_]+$',
                message=(
                    'Слаг может состоять только из цифр/букв и знака "_"!'
                ),
            )
        ],
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        """
        Строковое представление тега.
        """
        return f'{self.name}'


class Ingredient(models.Model):
    """
    Ингредиент для рецепта.
    """

    name = models.CharField(
        verbose_name='Название',
        help_text='Введите название ингредиента',
        max_length=200,
        unique=True,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения',
        max_length=200,
    ) 

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        """
        Строковое представление ингредиента.
        """
        return f'{self.name}'


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
    
    def __repr__(self) -> str:
        """
        Формальное строковое представление подписки.
        """

        return (
            f'{self.__class__.__name__}'
            f'(subscriber={self.subscriber}, publisher={self.publisher})'
        )
