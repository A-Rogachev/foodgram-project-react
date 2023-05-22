from api.utils import Base64ImageField
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, Subscription, Tag)
from rest_framework import serializers

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для модели User (пользователь).
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = ('is_subscribed', )

    def get_is_subscribed(self, user_obj):
        """
        Возвращает true/false в зависимости, от того, является ли
        текущий пользователь подписчиком.
        """
        return bool(
            Subscription.objects.filter(
                subscriber=self.context.get('request').user,
                publisher=user_obj.pk
            )
        )


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tag (тег для рецепта).
    """

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient (ингредиент для рецепта).
    """

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientSerializerWithMeasurement(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient (ингредиент для рецепта),
    использующийся в запросах рецептов.
    """

    id = serializers.ReadOnlyField(source='ingredient.pk')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Recipe (рецепты).
    """
    
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientSerializerWithMeasurement(
        read_only=True,
        many=True,
        source='ingredients_amount'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, recipe_obj):
        return bool(
            FavoriteRecipe.objects.filter(
                user=self.context.get('request').user,
                recipe=recipe_obj,
            )
        )
    
    def get_is_in_shopping_cart(self, obj):
        return False


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления/удаления рецепта из списка избранного.
    """

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = ('__all__', )
