from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from recipes.models import FavoriteRecipe, ShoppingCart, Tag

User = get_user_model()


class RecipesFilter(filters.FilterSet):
    """
    Набор фильтров для модели Recipe (Рецепт).
    """
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )

    def get_is_favorited(self, queryset, filter_name, filter_value):
        """
        Выдает рецепты, находящиеся в избранном пользователя.
        """
        favorites_ids = FavoriteRecipe.objects.filter(
            user=self.request.user.pk
        ).values_list('recipe', flat=True)
        if filter_value:
            return queryset.filter(pk__in=favorites_ids)
        return queryset.exclude(pk__in=favorites_ids)

    def get_is_in_shopping_cart(self, queryset, filter_name, filter_value):
        """
        Выдает рецепты, находящиеся в списке покупок пользователя.
        """
        shopping_cart_ids = ShoppingCart.objects.filter(
            user=self.request.user.pk
        ).values_list('recipe', flat=True)
        if filter_value:
            return queryset.filter(pk__in=shopping_cart_ids)
        return queryset.exclude(pk__in=shopping_cart_ids)
