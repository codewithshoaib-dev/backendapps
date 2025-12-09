from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Workspace, WorkspaceMembership, Project
from .serializers import WorkspaceSerializer, WorkspaceCreateSerializer, MembershipSerializer, ProjectSerializer
from .permissions import IsWorkspaceMember, IsWorkspaceAdminOrOwner
from .filter_backends import WorkspaceFilterBackend
from rest_framework.permissions import IsAuthenticated

class WorkspaceViewSet(viewsets.ModelViewSet):
    queryset = Workspace.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = WorkspaceSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return WorkspaceCreateSerializer
        return WorkspaceSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsWorkspaceAdminOrOwner])
    def invite_user(self, request, pk=None):
        workspace = self.get_object()
        email = request.data.get('email')
        try:
            user = __import__('django.contrib.auth').contrib.auth.get_user_model().objects.get(email=email)
        except Exception:
            return Response({'detail': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        membership, created = WorkspaceMembership.objects.get_or_create(user=user, workspace=workspace)
        serializer = MembershipSerializer(membership, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class MembershipViewSet(viewsets.ModelViewSet):
    queryset = WorkspaceMembership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated, IsWorkspaceAdminOrOwner]
    filter_backends = [WorkspaceFilterBackend]

    def perform_create(self, serializer):
        serializer.save(workspace=self.request.workspace)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    filter_backends = [WorkspaceFilterBackend]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
