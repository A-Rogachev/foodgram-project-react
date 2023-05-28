from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from api.paginators import PageNumberPaginationWithLimit
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (FoodgramUserSerializer, FavoriteRecipeSerializer,
                             IngredientSerializer, RecipeSerializer,
                             ShoppingCartSerializer, SubscriptionSerializer,
                             TagSerializer)
from api.filters import RecipesFilter
from api.utils import create_request_obj, delete_request_obj
from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class FoodgramUserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с моделью User (пользователь).
    """

    queryset = User.objects.all()
    serializer_class = FoodgramUserSerializer
    pagination_class = PageNumberPaginationWithLimit

    def get_permissions(self):
        """
        Определяет доступ в зависимости от аутентификации пользователя.
        """
        if self.action in ('retrieve', 'me', 'subscriptions'):
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthorOrAdminOrReadOnly]
        return [permission() for permission in permission_classes]

    @action(
        ['POST'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(
                serializer.validated_data['new_password'],
            )
            self.request.user.save()
            return Response(
                'Пароль успешно изменен',
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        ['GET'],
        detail=False,
        permission_classes=(IsAuthenticated, ),
    )
    def me(self, request, *args, **kwargs):
        """
        Персональная страница пользователя.
        """
        return Response(self.serializer_class(request.user).data)

    @action(
        ['GET'],
        detail=False,
        permission_classes=(IsAuthenticated, ),
    )
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

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, pk):
        """
        Подписка/отписка на автора рецепта.
        """
        request_publisher = get_object_or_404(User, pk=pk)
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
    permission_classes = (AllowAny, )


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    Вьюсет для работы с моделью Ingredient (ингредиент для рецепта).
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny, )


class RecipeViewset(viewsets.ModelViewSet):
    """
    Вьюсет для работы с моделью Recipe (рецепт).
    """

    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPaginationWithLimit
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipesFilter

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
        if not current_user.shopping_recipe.exists():
            return Response(
                {'errors': 'Ваш список покупок пуст!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            shopping_recipes = Recipe.objects.filter(
                pk__in=[
                    ShoppingCart.objects.filter(
                        user=self.request.user.pk
                    ).values_list('recipe', flat=True)
                ]
            ).values_list('pk', flat=True)
            shopping_ingredients = IngredientAmount.objects.filter(
                recipe__in=shopping_recipes,
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).annotate(
                Sum('amount', distinct=True)
            )

            date_of_loading_list = datetime.now().strftime("%d.%m.%Y (%H:%M)")
            new_shopping_list = []
            new_shopping_list.append('Пользователь: ' + current_user.username)
            new_shopping_list_name = (
                f'Список покупок на {date_of_loading_list}'
            )
            new_shopping_list.append(new_shopping_list_name)
            new_shopping_list.append('-' * len(new_shopping_list_name) + '\n')
            for ingredient in shopping_ingredients:
                new_shopping_list.append(
                    (
                        f'* {ingredient.get("ingredient__name")} '
                        f'({ingredient.get("ingredient__measurement_unit")})'
                        + f' - {ingredient.get("amount__sum")}'
                    )
                )
            new_shopping_list.append(
                f'\nсервис "Продуктовый помощник" {datetime.now().year} г.'
            )
            response = HttpResponse(
                content='\n'.join(new_shopping_list),
                content_type='text/plain; charset=UTF-8',
            )
            response['Content-Disposition'] = (
                f'attachment; filename=Shopping List '
                f'({current_user.username}) {date_of_loading_list}.txt'
            )
            return response
