from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, Subscription, Tag, ShoppingCart)
from rest_framework import serializers
from api.validators import validate_tags, validate_ingredients
from django.db import transaction
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
        return Subscription.objects.filter(
            subscriber=self.context.get('request').user,
            publisher=user_obj.pk
        ).exists()


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
        return FavoriteRecipe.objects.filter(
            user=self.context.get('request').user,
            recipe=recipe_obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return False

    def validate(self, data):
        """
        Валидация данных при POST/PATCH запросе.
        """
        tags_for_recipe = self.initial_data.get('tags')
        validate_tags(tags_for_recipe)

        ingredients_for_recipe = self.initial_data.get('ingredients')
        validate_ingredients(ingredients_for_recipe)
        
        data.update(
            {
                'tags': tags_for_recipe,
                'ingredients': ingredients_for_recipe,
                'author': self.context.get('request').user,
            }
        )
        return data

    @staticmethod
    def create_ingredients(ingredients, recipe):
        """
        Создает новые ингредиенты (модель IngredientAmount) при
        создании/обновлении рецепта.
        """
        new_ingredients = []
        for ingredient in ingredients:
                new_ingredients.append(
                    IngredientAmount(
                        recipe=recipe,
                        ingredient=Ingredient.objects.get(
                            pk=ingredient.get('id')
                        ),
                        amount=ingredient.get('amount'),
                    )
                )
        IngredientAmount.objects.bulk_create(new_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        """
        Добавление нового рецепта.
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        """
        Обновление рецепта.
        """
        tags = validated_data.pop('tags')
        recipe.tags.clear()
        recipe.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        recipe.ingredients.clear()
        self.create_ingredients(ingredients, recipe)

        return super().update(recipe, validated_data)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления/удаления рецепта из списка избранного.
    Также используется для вывода рецептов, на автора которых 
    подписан пользователь и добавления рецепта в список покупок.
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


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписки/отписки на авторов.
    """

    email = serializers.ReadOnlyField(source='publisher.email')
    id = serializers.ReadOnlyField(source='publisher.id')
    username = serializers.ReadOnlyField(source='publisher.username')
    first_name = serializers.ReadOnlyField(source='publisher.first_name')
    last_name = serializers.ReadOnlyField(source='publisher.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='publisher.recipes.count')
    is_subscribed = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        """
        Рецепты автора, на которого подписан пользователь.
        """
        request = self.context.get('user_request')
        limit_of_objects_on_page = request.query_params.get('recipes_limit')
        
        recipes = obj.publisher.recipes.all()
        if limit_of_objects_on_page:
            recipes = recipes[:int(limit_of_objects_on_page)]
        serializer = FavoriteRecipeSerializer(recipes, many=True)
        return serializer.data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с моделью ShoppingCart (список покупок).
    """

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def to_representation(self, instance):
        """
        Возвращает сериализатор рецепта для записи.
        """
        return FavoriteRecipeSerializer(instance).data
