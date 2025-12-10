from rest_framework import permissions
from .models import WorkspaceMembership, Workspace

class IsWorkspaceMember(permissions.BasePermission):
    def has_permission(self, request, view):
        workspace = getattr(request, 'workspace', None)
        user = request.user if request.user and request.user.is_authenticated else None
        if not workspace or not user:
            return False
        return WorkspaceMembership.objects.filter(workspace=workspace, user=user, is_active=True).exists()

class IsWorkspaceAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        workspace_id = view.kwargs.get("pk") or view.kwargs.get("workspace_id")
        if not workspace_id:
            return False

        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            return False

        membership = (
            WorkspaceMembership.objects
            .filter(workspace=workspace, user=user, is_active=True)
            .values_list("role", flat=True)
            .first()
        )

        return membership in (
            WorkspaceMembership.ROLE_ADMIN,
            WorkspaceMembership.ROLE_OWNER,
        )
