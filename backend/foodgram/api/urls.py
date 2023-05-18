from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, IngredientViewSet, TagViewSet

router = DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
