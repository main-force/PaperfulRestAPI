from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.authentication import TokenAuthentication, BaseAuthentication


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

class BaseIsOwnerOrReadOnlyWithQueryParams(BasePermission):
    query_params = {}

    def has_object_permission(self, request, view, obj):
        has_permission = True
        for key in [ele for ele in self.query_params.keys() if(ele in request.query_params.keys())]:
            if request.query_params[key] in self.query_params[key]:
                if request.user.is_authenticated:
                    if request.user.is_staff:
                        pass
                    elif hasattr(obj, 'user'):
                        has_permission = has_permission and (obj.user == request.user)
                    elif hasattr(obj, 'writer'):
                        has_permission = has_permission and (obj.writer.user == request.user)
                    elif obj.__class__ == get_user_model():
                        has_permission = has_permission and (obj.id == request.user.id)
                    else:
                        return False
                else:
                    return False
        if request.method in SAFE_METHODS:
            pass
        else:
            if request.user.is_authenticated:
                if request.user.is_staff:
                    pass
                elif hasattr(obj, 'user'):
                    has_permission = has_permission and (obj.user == request.user)
                elif hasattr(obj, 'writer'):
                    has_permission = has_permission and (obj.writer.user == request.user)
                elif obj.__class__ == get_user_model():
                    has_permission = has_permission and (obj.id == request.user.id)
                else:
                    return False
            else:
                return False

        return has_permission

class IsOwnerOrReadOnlyWithPostStatus(BaseIsOwnerOrReadOnlyWithQueryParams):
    query_params = {'status': ['T', 'P', 'B']}
