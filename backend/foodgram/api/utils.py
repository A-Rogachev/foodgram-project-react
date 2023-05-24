from rest_framework import status
from rest_framework.response import Response


def create_request_obj(request_obj,
                       model_class,
                       serializer,
                       user_args,
                       messages):
    """
    Создает необходимый объект в БД; используется при 
    добавлении рецепта в список покупок, добавлении рецепта в 
    избранное.
    """
    already_existed, created = model_class.objects.get_or_create(**user_args)
    if not created:
        return Response(
            {'errors': messages.get('post_failure_repeating')},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(
        serializer(request_obj).data,
        status=status.HTTP_201_CREATED,
    )


def delete_request_obj(model_class,
                       user_args,
                       messages):
    """
    Удаляет объект из базы данных; используется при удалении
    рецепта из корзины покупок; удаление рецепта из списка избранного,
    отписки от автора рецепта.
    """
    try:
        model_obj = model_class.objects.get(**user_args)
    except model_class.DoesNotExist:
        return Response(
            {'errors': messages.get('delete_failure_404')},
            status=status.HTTP_400_BAD_REQUEST,
        )
    model_obj.delete()
    return Response(
        {'detail': messages.get('delete_success')},
        status=status.HTTP_204_NO_CONTENT,
    )
