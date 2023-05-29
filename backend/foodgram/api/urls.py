from django.urls import include, path, re_path
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.routers import DefaultRouter

from api.views import (FoodgramUserViewSet, IngredientViewSet, RecipeViewset,
                       TagViewSet)

router = DefaultRouter()
router.register('users', FoodgramUserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewset)

urlpatterns = [
    re_path(
        r'^users/me/$',
        DjoserUserViewSet.as_view({'get': 'me'}),
        name='user-me',
    ),
    re_path(
        r'^users/set_password/$',
        DjoserUserViewSet.as_view({'post': 'set_password'}),
        name='user-set-password',
    ),
    path(
        '',
        include(router.urls),
    ),
    re_path(
        r'^auth/',
        include('djoser.urls.authtoken'),
    ),
]
