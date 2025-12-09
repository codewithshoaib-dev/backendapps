from rest_framework.filters import BaseFilterBackend

class WorkspaceFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        workspace = getattr(request, 'workspace', None)
        if workspace is None:
            return queryset.none()
        if hasattr(queryset, 'for_workspace'):
            return queryset.for_workspace(workspace)
        return queryset.filter(workspace=workspace)
