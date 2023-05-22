from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, Subscription,
                            Tag)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .serializers import (CustomUserSerializer, FavoriteRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет для работы с моделью User (пользователь).
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination
    # lookup_field = 'username'
    # permission_classes = (IsAdmin, )
    # filter_backends = (filters.SearchFilter, )
    # search_fields = ('username', )
    
    @action(['GET'], detail=False)
    def me(self, request, *args, **kwargs):
        """
        Персональная страница пользователя.
        """
        return Response(self.serializer_class(request.user).data)

    @action(['GET'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        """
        Возвращает всех авторов, чьим подписчиком является пользователь.
        """
        publishers_ids = Subscription.objects.filter(
            subscriber=request.user.pk
        ).values_list('publisher', flat=True)
        publishers = User.objects.filter(pk__in=publishers_ids).all()

        paginator = PageNumberPagination()
        serializer = self.serializer_class(
            publishers,
            many=True
        )
        paginator.paginate_queryset(publishers, request)
        return paginator.get_paginated_response(serializer.data)


class TagViewSet(mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):
    """
    Вьюсет для работы с моделью Tag (тег для рецепта).
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    Вьюсет для работы с моделью Ingredient (ингредиент для рецепта).
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewset(viewsets.ModelViewSet):
    """
    Вьюсет для работы с моделью Recipe (рецепт).
    """

    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = RecipeSerializer

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        """
        Добавление/удаление рецепта в/из списка избранных.
        """
        current_recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            favorite, created = FavoriteRecipe.objects.get_or_create(
                user=request.user,
                recipe=current_recipe,
            )
            if not created:
                return Response(
                    {'errors': 'Рецепт уже находится в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                serializer = FavoriteRecipeSerializer(current_recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )
        elif request.method == 'DELETE':
            try:
                favorite_recipe = FavoriteRecipe.objects.get(
                    user=request.user,
                    recipe=current_recipe,
                )
            except FavoriteRecipe.DoesNotExist:
                return Response(
                    {'errors': 'Рецепта нет в списке избранного!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            favorite_recipe.delete()
            return Response(
                {'detail': 'Рецепт успешно удален из избранного'},
                status=status.HTTP_204_NO_CONTENT,
            )
