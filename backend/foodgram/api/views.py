from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Subscription, Tag)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .paginators import PageNumberPaginationWithLimit
from .serializers import (CustomUserSerializer, FavoriteRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          TagSerializer)
from .utils import create_request_obj, delete_request_obj

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет для работы с моделью User (пользователь).
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPaginationWithLimit

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
        new_args = {
            'subscriber': request.user,
            'publisher': request_publisher,
        }
        if request.method == 'POST':
            if request.user == request_publisher:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscription, created = Subscription.objects.get_or_create(
                **new_args
            )
            if not created:
                return Response(
                    {'errors': 'Нельзя подписаться повторно!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                serializer = SubscriptionSerializer(
                    subscription,
                    context={'user_request': request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )
        elif request.method == 'DELETE':
            return delete_request_obj(
                model_class=Subscription,
                user_args=new_args,
                messages=settings.SUBSCRIBE_MESSAGES,
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
            self.queryset = self.queryset.filter(
                favorite_list__user=self.request.user
            )
        elif is_favorited == '0':
            self.queryset = self.queryset.exclude(
                favorite_list__user=self.request.user
            )
        
        tags = self.request.query_params.getlist('tags')
        if tags:
            self.queryset = self.queryset.filter(tags__slug__in=tags)
        
        return self.queryset


    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        """
        Добавление/удаление рецепта в/из списка избранных.
        """
        request_recipe = get_object_or_404(Recipe, pk=pk)
        new_args = {
            'user': request.user,
            'recipe': request_recipe,
        }
        if request.method == 'POST':
            return create_request_obj(
                request_obj=request_recipe,
                model_class=FavoriteRecipe,
                serializer=FavoriteRecipeSerializer,
                user_args=new_args,
                messages=settings.FAVORITES_MESSAGES,
            )
        elif request.method == 'DELETE':
            return delete_request_obj(
                model_class=FavoriteRecipe,
                user_args=new_args,
                messages=settings.FAVORITES_MESSAGES,
            )

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        """
        Добавляет/удаляет рецепт из списка покупок.
        """
        request_recipe = get_object_or_404(Recipe, pk=pk)
        new_args = {
            'user': request.user,
            'recipe': request_recipe,
        }
        if request.method == 'POST':
            return create_request_obj(
                request_obj=request_recipe,
                model_class=ShoppingCart,
                serializer=ShoppingCartSerializer,
                user_args=new_args,
                messages=settings.SHOPPING_CART_MESSAGES,
            )
        elif request.method == 'DELETE':
            return delete_request_obj(
                model_class=ShoppingCart,
                user_args=new_args,
                messages=settings.SHOPPING_CART_MESSAGES,
            )

    @action(methods=['GET'], detail=False)
    def download_shopping_cart(self, request):
        """
        Скачивание списка покупок файлом в формате ".txt".
        """

        current_user = User.objects.get(pk=self.request.user.pk)
        if not current_user.shopping.exists():
            return Response(
                {'errors': 'Ваш список покупок пуст!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:

            shopping_ingredients = IngredientAmount.objects.filter(
                recipe__shopping__user=current_user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).annotate(
                Sum('amount', distinct=True)
            )

            print(shopping_ingredients)
            return Response(
                {'detail': 'spisok est'}
            )

        