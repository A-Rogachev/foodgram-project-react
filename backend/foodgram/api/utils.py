from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

SUBSCRIBE_MESSAGES = {
    'post_failure_repeating': 'Нельзя подписаться повторно!',
    'delete_failure_404': 'На данного пользователя подписка не оформлена!',
    'delete_success': 'Подписка успешно отменена!',
}




def create_request_obj(request_obj,
                       model_class,
                       serializer,
                       user_args,
                       messages):
    """
    Создает необходимый объект в БД; используется при 
    добавлении рецепта в список покупок, избранное.
    """
    already_existed, created = model_class.objects.get_or_create(**user_args)
    if not created:
        return Response(
            {'errors': messages.get('post_failure_repeating')},
            status=status.HTTP_400_BAD_REQUEST,
        )
    else:
        return Response(
            serializer(request_obj).data,
            status=status.HTTP_201_CREATED,
        )

def delete_request_obj(model_class,
                       user_args,
                       messages):
    """
    Удаляет объект из базы данных; используется при удалении
    рецепта из корзины покупок, списка избранного.
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


# @action(methods=['POST', 'DELETE'], detail=True)
#     def subscribe(self, request, id):
#         """
#         Подписка/отписка на автора рецепта.
#         """

#         request_publisher = get_object_or_404(User, pk=id)
#         if request.method == 'POST':
#             if request.user == request_publisher:
#                 return Response(
#                     {'errors': 'Нельзя подписаться на самого себя!'},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#             subscripion, created = Subscription.objects.get_or_create(
#                 subscriber=request.user,
#                 publisher=request_publisher,
#             )
#             if not created:
#                 return Response(
#                     {'errors': 'Нельзя подписаться повторно!'},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#             else:
#                 serializer = SubscriptionSerializer(
#                     subscripion,
#                     context={'user_request': request}
#                 )
#                 return Response(
#                     serializer.data,
#                     status=status.HTTP_201_CREATED,
#                 )
#         elif request.method == 'DELETE':
#             try:
#                 request_subscription = Subscription.objects.get(
#                     subscriber=request.user,
#                     publisher=request_publisher,
#                 )
#             except Subscription.DoesNotExist:
#                 return Response(
#                     {
#                         'errors': (
#                             'На данного пользователя подписка не оформлена!'
#                         )
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#             request_subscription.delete()
#             return Response(
#                 {'detail': 'Подписка успешно отменена!'},
#                 status=status.HTTP_204_NO_CONTENT,
#             )


