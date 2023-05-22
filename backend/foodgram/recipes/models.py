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

    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
    )
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
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Введите время приготовления по рецепту',
        default=1,
        validators=[
            MinValueValidator(1),
        ]
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение для рецепта',
        help_text='Загрузите изображение рецепта',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        related_name='recipes',
        through='IngredientAmount',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
        verbose_name='Тег',
        help_text='Выберите тег',
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
        related_name='ingredients_amount',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredients_amount',
        on_delete=models.PROTECT,
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
        return (
            f'{self.ingredient} ({self.ingredient.measurement_unit}) - '
            f'{self.amount}'
        )


class FavoriteRecipe(models.Model):
    """
    Модель списка избранных рецептов.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_list',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_list',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique favorite_list'
            ),
        ]

    def __str__(self):
        """
        Строковое представление избранных рецептов.
        """
        return (
            f'{self.user} - "{self.recipe}"'
        )
