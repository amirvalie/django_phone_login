from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        return bool(not request.user and not request.user.is_authenticated)