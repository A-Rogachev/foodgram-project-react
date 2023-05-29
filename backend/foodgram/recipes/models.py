from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from recipes.validators import validate_for_nonpunctuation_marks

User = get_user_model()


class Tag(models.Model):
    """
    Метка для фильтрации рецептов.
    """

    name = models.CharField(
        verbose_name='Название',
        help_text='Введите название тега',
        max_length=settings.LIMIT_TAG_INGREDIENT_RECIPE_SLUG_NAME,
        validators=[
            validate_for_nonpunctuation_marks,
        ],
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цвет виджета тега',
        help_text='Выберите цвет для тега',

    )
    slug = models.SlugField(
        verbose_name='Слаг тега',
        help_text='Введите слаг для тега',
        unique=True,
        max_length=settings.LIMIT_TAG_INGREDIENT_RECIPE_SLUG_NAME,
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
        max_length=settings.LIMIT_TAG_INGREDIENT_RECIPE_SLUG_NAME,
        db_index=True,
        validators=[
            validate_for_nonpunctuation_marks,
        ],
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения',
        max_length=settings.LIMIT_TAG_INGREDIENT_RECIPE_SLUG_NAME,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            ),
        ]

    def __str__(self) -> str:
        """
        Строковое представление ингредиента.
        """
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """
    Модель рецепта.
    """

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
        validators=[
            validate_for_nonpunctuation_marks,
        ],
    )
    name = models.CharField(
        verbose_name='Название',
        help_text='Введите название рецепта',
        unique=True,
        max_length=settings.LIMIT_TAG_INGREDIENT_RECIPE_SLUG_NAME,
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
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['pub_date']

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
        on_delete=models.PROTECT,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Выберите количество ингредиента',
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(settings.LIMIT_INGREDIENT_AMOUNT),
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
        related_name='favorite_recipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
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


class ShoppingCart(models.Model):
    """
    Модель для списка покупок.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_item'
            ),
        ]

    def __str__(self) -> str:
        """
        Строковое представление рецепта в списке покупок.
        """
        return (
            f'Рецепт "{self.recipe}" находится в списке покупок'
            f' пользователя "{self.user}"'
        )
