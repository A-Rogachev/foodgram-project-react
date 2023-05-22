from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Subscription, Tag

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
