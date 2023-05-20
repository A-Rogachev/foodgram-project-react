from django.contrib import admin

from recipes.models import Ingredient, Subscription, Tag


admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Subscription)
