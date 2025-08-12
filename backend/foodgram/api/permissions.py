from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission

from constants import HTTP_METHOD_NOT_ALLOWED


class IsAdminOrReadOnly(BasePermission):
    """Проверяет права доступа: чтение для всех, запись только для админов."""

    message = "Метод запрещен для не-администраторов"

    def has_permission(self, request, view):
        """Проверяет общие права доступа к view."""
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated and request.user.is_staff:
            raise PermissionDenied(
                detail=self.message, code=HTTP_METHOD_NOT_ALLOWED,
            )
        return True


class IsAuthorOrStaff(BasePermission):
    """Проверяет права доступа: автор объекта или администратор."""

    def has_object_permission(self, request, view, obj):
        """Проверяет права доступа к конкретному объекту."""
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
