from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Право доступа для автора, администратора - в другом случае только чтение.
    """

    def has_permission(self, request, view):
        """
        Запрос только на чтение, либо для аутентифицированного юзера.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """
        Объект доступен для ред-ия автором или администратором.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_supersuser
        )
