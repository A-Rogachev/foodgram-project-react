from django.contrib.auth import get_user_model
from django.shortcuts import render
from djoser.views import UserViewSet
from recipes.models import Tag
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .serializers import CustomUserSerializer, TagSerializer

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


class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с моделью Tag (тег для рецепта).
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
