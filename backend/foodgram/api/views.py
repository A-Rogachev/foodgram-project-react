from api.paginators import PageNumberPaginationWithLimit
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, Subscription,
                            Tag, ShoppingCart)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .serializers import (CustomUserSerializer, FavoriteRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет для работы с моделью User (пользователь).
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPaginationWithLimit
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
        publishers = request.user.subscriber.all()
        serializer = SubscriptionSerializer(
            self.paginate_queryset(publishers),
            many=True,
            context={'user_request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, id):
        """
        Подписка/отписка на автора рецепта.
        """
        request_publisher = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            if request.user == request_publisher:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscripion, created = Subscription.objects.get_or_create(
                subscriber=request.user,
                publisher=request_publisher,
            )
            if not created:
                return Response(
                    {'errors': 'Нельзя подписаться повторно!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                serializer = SubscriptionSerializer(
                    subscripion,
                    context={'user_request': request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )
        elif request.method == 'DELETE':
            try:
                request_subscription = Subscription.objects.get(
                    subscriber=request.user,
                    publisher=request_publisher,
                )
            except Subscription.DoesNotExist:
                return Response(
                    {
                        'errors': (
                            'На данного пользователя подписка не оформлена!'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request_subscription.delete()
            return Response(
                {'detail': 'Подписка успешно отменена!'},
                status=status.HTTP_204_NO_CONTENT,
            )


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
    pagination_class = PageNumberPaginationWithLimit
        
    def get_queryset(self):
        """
        Возвращает список объектов в зависимости от переданных аргументов.
        """
        author_id = self.request.query_params.get('author')
        if author_id:
            self.queryset = self.queryset.filter(
                author=get_object_or_404(User, pk=author_id)
            )
        
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1':
            self.queryset = self.queryset.filter(favorite_list__user=self.request.user)
        elif is_favorited == '0':
            self.queryset = self.queryset.exclude(favorite_list__user=self.request.user)
        
        tags = self.request.query_params.getlist('tags')
        if tags:
            self.queryset = self.queryset.filter(tags__slug__in=tags)
        
        return self.queryset


    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        """
        Добавление/удаление рецепта в/из списка избранных.
        """
        current_recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            _, created = FavoriteRecipe.objects.get_or_create(
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

    def shopping_cart(self, request, pk):
        ...