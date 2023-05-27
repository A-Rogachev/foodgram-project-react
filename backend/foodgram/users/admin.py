from django.contrib import admin
from django.contrib.auth import get_user_model
from rest_framework.authtoken.admin import TokenProxy

from users.models import Subscription

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    """
    Админ-класс с настройками для модели пользователя.
    """
    list_display = ('username', 'email')
    list_filter = ('username', 'email')
    search_fields = ('email',)


class SubscriptionAdmin(admin.ModelAdmin):
    """
    Админ-класс с настройками для модели Subscription.
    """
    list_display = ('publisher', 'subscriber')
    list_filter = ('publisher',)
    search_fields = ('publisher__username',)


admin.site.register(User, admin_class=UserAdmin)
admin.site.register(Subscription, admin_class=SubscriptionAdmin)
admin.site.unregister(TokenProxy)
