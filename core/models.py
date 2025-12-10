from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()



class Workspace(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_workspaces')

    class Meta:
        indexes = [models.Index(fields=['slug']), models.Index(fields=['name'])]

    def __str__(self):
        return self.name

class WorkspaceMembership(models.Model):
    ROLE_OWNER = 'owner'
    ROLE_ADMIN = 'admin'
    ROLE_MEMBER = 'member'
    ROLE_CHOICES = [(ROLE_OWNER, 'Owner'), (ROLE_ADMIN, 'Admin'), (ROLE_MEMBER, 'Member')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspace_memberships')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'workspace')
        indexes = [models.Index(fields=['workspace', 'user']), models.Index(fields=['workspace', 'role'])]

    def __str__(self):
        return f'{self.user_id}@{self.workspace_id}:{self.role}'

class WorkspaceQuerySet(models.QuerySet):
    def for_workspace(self, workspace):
        if workspace is None:
            return self.none()
        return self.filter(workspace_id=workspace.id)

class WorkspaceModel(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='+')
    objects = WorkspaceQuerySet.as_manager()

    class Meta:
        abstract = True

class Project(WorkspaceModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [models.Index(fields=['workspace', 'name'])]
