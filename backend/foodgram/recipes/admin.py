from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Subscription, Tag)


class RecipeIngredientInline(admin.TabularInline):
    """
    Позволяет добавлять ингредиенты при создании рецепта
    в админ-панели.
    """
    model = IngredientAmount


class IngredientAdmin(admin.ModelAdmin):
    """
    Админ-класс с настройками для модели Ingredient.
    """
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    """
    Админ-класс с настройками для модели Recipe.
    """
    inlines = [RecipeIngredientInline]
    list_display = ('name', 'author', 'in_favorite_list')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', )

    class Meta:
        model = Recipe

    def in_favorite_list(self, obj):
        """
        Общее число добавлений рецепта в избранное.
        """
        return obj.favorite_list.count()

    in_favorite_list.short_description = 'Число добавления в избранное'


class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Админ-класс с настройками для модели ShoppingCart.
    """
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user__username',)


class TagAdmin(admin.ModelAdmin):
    """
    Админ-класс с настройками для модели Tag.
    """
    list_display = ('name', 'slug', 'color')
    list_filter = ('name',)
    search_fields = ('name',)


class FavoriteRecipeAdmin(admin.ModelAdmin):
    """
    Админ-класс с настройками для модели FavoriteRecipe.
    """
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user__username',)


class SubscriptionAdmin(admin.ModelAdmin):
    """
    Админ-класс с настройками для модели Subscription.
    """
    list_display = ('publisher', 'subscriber')
    list_filter = ('publisher',)
    search_fields = ('publisher__username',)


admin.site.register(Ingredient, admin_class=IngredientAdmin)
admin.site.register(Tag, admin_class=TagAdmin)
admin.site.register(Recipe, admin_class=RecipeAdmin)
admin.site.register(Subscription, admin_class=SubscriptionAdmin)
admin.site.register(ShoppingCart, admin_class=ShoppingCartAdmin)
admin.site.register(FavoriteRecipe, admin_class=FavoriteRecipeAdmin)
