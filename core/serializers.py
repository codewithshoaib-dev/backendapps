from rest_framework import serializers
from .models import Workspace, WorkspaceMembership, Project
from django.contrib.auth import get_user_model

User = get_user_model()

class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'slug', 'created_at', 'owner']

class WorkspaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ['name', 'slug']

    def create(self, validated_data):
        user = self.context['request'].user
        workspace = Workspace.objects.create(owner=user, **validated_data)
        WorkspaceMembership.objects.create(user=user, workspace=workspace, role=WorkspaceMembership.ROLE_OWNER)
        return workspace

class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = WorkspaceMembership
        fields = ['id', 'user', 'user_email', 'role', 'is_active', 'created_at']
        read_only_fields = ['created_at']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'workspace', 'name', 'description', 'created_by', 'created_at']
        read_only_fields = ['workspace', 'created_by', 'created_at']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['workspace'] = request.workspace
        validated_data['created_by'] = request.user
        return super().create(validated_data)
