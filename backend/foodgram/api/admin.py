from django.contrib import admin
from recipes.models import (Ingredient, IngredientAmount, Recipe, ShoppingCart,
                            Subscription, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientAmount


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]

    class Meta:
        model = Recipe

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Subscription)
admin.site.register(ShoppingCart)
