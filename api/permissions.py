from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):
    """
    Allows access only to not authenticated users.
    """
    def has_permission(self, request, view):
        return bool(request.user.is_anonymous and not request.user.is_authenticated)
