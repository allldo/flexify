from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

from constructor.models import CustomSite


class CustomPermission(BasePermission):
    @staticmethod
    def has_permission(request, view):
        if view.action in ('list', 'retrieve'):
            return True
        elif view.action in ('create', 'partial_update', 'update', 'destroy'):
            if request.user.is_authenticated:
                return True
            else:
                raise PermissionDenied("You must be authenticated to perform this action.")
        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ('create', 'update', 'partial_update', 'destroy'):
            return obj.owner == request.user
        return True


class IsSiteOwnerPermission(BasePermission):
    def has_permission(self, request, view):
        site_id = view.kwargs.get('site_id')
        if not site_id:
            return False
        try:
            site = CustomSite.objects.get(id=site_id)
            if site.user == request.user:
                return True
        except CustomSite.DoesNotExist:
            raise PermissionDenied("Site not found or you do not have access.")

        return False