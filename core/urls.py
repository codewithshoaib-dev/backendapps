from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, MembershipViewSet, ProjectViewSet

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')
router.register(r'memberships', MembershipViewSet, basename='membership')
router.register(r'projects', ProjectViewSet, basename='project')

urlpatterns = router.urls
