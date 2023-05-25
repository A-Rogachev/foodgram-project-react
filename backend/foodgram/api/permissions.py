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
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsAdmin(permissions.BasePermission):
    """Право доступа только для администратора."""

    def has_permission(self, request, view):
        "Запрос разрешен только для администратора."
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )

class IsAdminOrReadOnly(permissions.BasePermission):
    """Право доступа администратора. Иначе доступно для чтения."""

    def has_permission(self, request, view):
        "Запрос разрешен только для администратора - иначе только чтение."
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )