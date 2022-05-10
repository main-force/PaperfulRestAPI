from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS


class AllowAny(BasePermission):
    def has_permission(self, request, view):
        return True


class IsOwnerOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return True
            elif hasattr(obj, 'writer'):
                return obj.writer.user == request.user
            elif hasattr(obj, 'user'):
                return obj.user == request.user
            elif obj.__class__ == get_user_model():
                return obj.id == request.user.id
            return False
        else:
            return False


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            if request.user.is_authenticated:
                if request.user.is_staff:
                    return True
                elif hasattr(obj, 'user'):
                    return obj.user == request.user
                elif hasattr(obj, 'writer'):
                    return obj.writer.user == request.user
                elif obj.__class__ == get_user_model():
                    return obj.id == request.user.id
                return False
            else:
                return False
