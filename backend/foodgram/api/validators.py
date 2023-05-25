from recipes.models import Tag
from rest_framework import serializers


def validate_tags(tags_ids=None):
    """
    Проверяет корректность переданных тегов.
    """
    if tags_ids is None:
        raise serializers.ValidationError(
            'Не выбраны теги для рецепта!'
        )
    if len(set(tags_ids)) != len(tags_ids):
        raise serializers.ValidationError(
            'Теги не должны повторяться!'
        )
    for tag in tags_ids:
        try:
            Tag.objects.get(id=tag)
        except Tag.DoesNotExist:
            raise serializers.ValidationError(
                f'Тега с id {tag} не существует!'
            )


def validate_ingredients(ingredients=None):
    """
    Проверяет корректность переданных ингредиентов.
    """
    if ingredients is None:
        raise serializers.ValidationError(
            'Необходим хотя бы один ингредиент!'
        )
    ingredients_ids = [ingredient.get('id') for ingredient in ingredients]
    if len(set(ingredients_ids)) != len(ingredients_ids):
        raise serializers.ValidationError(
            'Ингридиенты должны иметь уникальный id!'
        )
    ingredients_amounts = [
        ingredient.get('amount') for ingredient in ingredients
    ]
    if any([int(amount) <= 0 for amount in ingredients_amounts]):
        raise serializers.ValidationError(
            'Минимальное количество ингридиента = 1!'
        )
