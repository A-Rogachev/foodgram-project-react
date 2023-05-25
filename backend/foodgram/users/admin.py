from django.contrib import admin
from django.contrib.auth import get_user_model
from rest_framework.authtoken.admin import TokenProxy

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    """
    Админ-класс с настройками для модели пользователя.
    """
    list_display = ('username', 'email')
    list_filter = ('username', 'email')
    search_fields = ('email',)


admin.site.register(User, admin_class=UserAdmin)
admin.site.unregister(TokenProxy)
