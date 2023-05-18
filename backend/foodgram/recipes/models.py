from django.db import models
from django.core.validators import RegexValidator


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
