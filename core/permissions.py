from rest_framework import permissions
from .models import WorkspaceMembership

class IsWorkspaceMember(permissions.BasePermission):
    def has_permission(self, request, view):
        workspace = getattr(request, 'workspace', None)
        user = request.user if request.user and request.user.is_authenticated else None
        if not workspace or not user:
            return False
        return WorkspaceMembership.objects.filter(workspace=workspace, user=user, is_active=True).exists()

class IsWorkspaceAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        workspace = getattr(request, 'workspace', None)
        user = request.user if request.user and request.user.is_authenticated else None
        if not workspace or not user:
            return False
        qs = WorkspaceMembership.objects.filter(workspace=workspace, user=user, is_active=True)
        if not qs.exists():
            return False
        role = qs.values_list('role', flat=True).first()
        return role in (WorkspaceMembership.ROLE_ADMIN, WorkspaceMembership.ROLE_OWNER)
