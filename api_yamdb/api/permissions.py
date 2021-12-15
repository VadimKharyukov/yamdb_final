from rest_framework.permissions import (BasePermission,
                                        SAFE_METHODS,
                                        IsAuthenticatedOrReadOnly
                                        )

from reviews.models import UserRoles


class IsAdmin(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        return (request.user.is_superuser
                or (request.auth and request.user.role == UserRoles.ADMIN))


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            return request.user.role == UserRoles.ADMIN
        return False


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsOwnerOrAdminOrModeratorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.role in [UserRoles.ADMIN, UserRoles.MODERATOR]
                )
