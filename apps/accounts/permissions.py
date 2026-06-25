from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow all authenticated users access
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admins get access to everything
        if request.user.is_staff:
            return True
        # Members can only access their own account
        return obj.user == request.user