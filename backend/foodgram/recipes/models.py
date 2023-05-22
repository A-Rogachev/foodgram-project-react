from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

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


class Recipe(models.Model):
    """
    Модель рецепта.
    """

    name = models.CharField(
        verbose_name='Название',
        help_text='Введите название рецепта',
        unique=True,
        max_length=200,
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание рецепта',

    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Введите время приготовления по рецепту',
        default=2,
        validators=[
            MinValueValidator(2),
        ]
    )
    image = models.BinaryField(
        verbose_name='Картинка, закодированная в Base64',
        help_text='Загрузите изображение рецепта',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        related_name='recipes',
        through='IngredientAmount'
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        """
        Строковое представление рецепта.
        """
        return f'{self.name}'
    

class IngredientAmount(models.Model):
    """
    Промежуточная модель количества ингредиентов.
    """
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredients',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        help_text='Выберите количество ингредиента',
        default=1,
        validators=[
            MinValueValidator(1),
        ],
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'


    def __str__(self):
        """
        Строковое представление таблицы ингредиентов для рецептов.
        """
        return f'{self.recipe} - {self.ingredient} - {self.amount} {self.ingredient.measurement_unit} '
