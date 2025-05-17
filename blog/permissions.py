from rest_framework import permissions
# apps/blog/permissions.py
from rest_framework import permissions

class IsStaffOrAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to:
    - Allow public read access (GET, HEAD, OPTIONS).
    - Restrict POST to staff users.
    - Allow PUT/DELETE for staff or the post's author.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for all (public read access)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Require authentication for write actions
        if not request.user.is_authenticated:
            return False
        # Allow POST only for staff
        if view.action == 'create':
            return request.user.is_staff
        return True

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS for all
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow PUT/DELETE for staff or the post's author
        return request.user.is_staff or obj.author == request.user