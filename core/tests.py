import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from core.models import Workspace, WorkspaceMembership, Project

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='user1', email='user1@example.com', password='pass')

@pytest.fixture
def user2(db):
    return User.objects.create_user(username='user2', email='user2@example.com', password='pass')

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client(api_client, user):
    api_client.login(email='user1@example.com', password='pass')
    return api_client

@pytest.fixture
def workspace(user):
    ws = Workspace.objects.create(name='Acme', slug='acme', owner=user)
    WorkspaceMembership.objects.create(user=user, workspace=ws, role=WorkspaceMembership.ROLE_OWNER)
    return ws

def test_create_workspace(auth_client):
    url = reverse('workspace-list')
    payload = {'name': 'Team X', 'slug': 'team-x'}
    resp = auth_client.post(url, payload, format='json')
    assert resp.status_code == 201
    assert Workspace.objects.filter(slug='team-x').exists()

def test_workspace_scoping(auth_client, workspace):
    api_client = auth_client
    api_client.credentials(HTTP_X_WORKSPACE_ID=str(workspace.id))
    url = reverse('project-list')
    payload = {'name': 'Proj 1', 'description': 'desc'}
    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == 201
    p = Project.objects.get(name='Proj 1')
    assert p.workspace_id == workspace.id

def test_non_member_cannot_access(api_client, user2, workspace):
    api_client.login(email='user2@gmail.com', password='pass')
    api_client.credentials(HTTP_X_WORKSPACE_ID=str(workspace.id))
    url = reverse('project-list')
    resp = api_client.get(url)
    assert resp.status_code == 403

def test_admin_can_invite(auth_client, workspace, user2):
    api_client = auth_client
    url = reverse('workspace-invite-user', kwargs={'pk': workspace.id})
    payload = {'email': user2.email}
    resp = api_client.post(url, payload, format='json')
    print(resp)
    assert resp.status_code in (200, 201)
    assert WorkspaceMembership.objects.filter(user=user2, workspace=workspace).exists()
