from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class CustomPermission(BasePermission):
    @staticmethod
    def has_permission(request, view):
        if view.action in ('list', 'retrieve'):
            return True
        elif view.action in ('create', 'patch', 'put'):
            if request.user.is_authenticated:
                return True
            else:
                raise PermissionDenied("You must be authenticated to perform this action.")

        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ('update', 'partial_update', 'destroy'):
            return obj.owner == request.user
        return True