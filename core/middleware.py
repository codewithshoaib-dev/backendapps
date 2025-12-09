from django.utils.deprecation import MiddlewareMixin
from .models import Workspace

class WorkspaceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        workspace_id = request.headers.get('X-Workspace-Id') or request.GET.get('workspace_id')
        request.workspace = None
        if workspace_id:
            try:
                request.workspace = Workspace.objects.get(pk=workspace_id)
            except Workspace.DoesNotExist:
                request.workspace = None
