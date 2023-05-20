from django.contrib.auth import get_user_model
from django.shortcuts import render
from djoser.views import UserViewSet
from recipes.models import Ingredient, Subscription, Tag
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .serializers import (CustomUserSerializer, IngredientSerializer, 
                          TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет для работы с моделью User (пользователь).
    """

    # http_method_names = ['get', 'post', 'head', 'patch', 'delete']
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


class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с моделью Tag (тег для рецепта).
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с моделью Ingredient (ингредиент для рецепта).
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
