from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model

from recipes.models import Tag

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
        if filter_value:
            return queryset.filter(favorite_list__user=self.request.user)
        return queryset.exclude(favorite_list__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, filter_name, filter_value):
        """
        Выдает рецепты, находящиеся в списке покупок пользователя.
        """
        if filter_value:
            return queryset.filter(shopping__user=self.request.user)
        return queryset.exclude(shopping__user=self.request.user)
