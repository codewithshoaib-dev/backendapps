from typing import Iterable, Optional
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class RolePermission(BasePermission):
    """
    Role-based access control for DRF views.

    Usage:
        class MyView(APIView):
            permission_classes = [RolePermission]
            required_roles = ["admin", "manager"]
            require_all_roles = False  # default: any of these roles allowed
    """

    # Whether all roles are required (vs any)
    require_all_roles = False
    # Whether to let staff/superuser bypass role checks
    allow_staff = True

    def _get_required_roles(self, view: APIView) -> Optional[Iterable[str]]:
        """
        Get the list of required roles from the view.
        Returns None if the view doesn't define `required_roles`.
        Empty list [] means "no specific roles required" (allowed).
        """
        if not hasattr(view, "required_roles"):
            return None
        roles = getattr(view, "required_roles")
        return list(roles) if roles is not None else None

    def _user_roles_set(self, user) -> set:
        """
        Return the user's roles as a set of role names.
        Works for both queryset-based roles (ManyToMany)
        and simple iterable attributes (e.g. ['admin', 'user']).
        """
        roles = getattr(user, "roles", None)
        if not roles:
            return set()
        try:
            return set(roles.values_list("name", flat=True))
        except Exception:
            return set(roles)

    def has_permission(self, request: Request, view: APIView) -> bool:  # type: ignore[override]
        """
        Main DRF permission check.
        Order of checks:
            1. Reject anonymous users
            2. Allow staff/superuser (if allow_staff=True)
            3. Get required roles from the view
            4. Compare user roles vs required roles
        """
        user = request.user
        if not getattr(user, "is_authenticated", False):
            return False

        if self.allow_staff and (user.is_superuser or user.is_staff):
            return True

        required = self._get_required_roles(view)
        # If view doesn’t define required_roles → deny access by default
        if required is None:
            return False

        user_roles = self._user_roles_set(user)
        required_set = set(required)

        # If view or class requires all roles, enforce that
        if getattr(view, "require_all_roles", self.require_all_roles):
            return required_set.issubset(user_roles)

        # Default: allow if user has at least one required role
        return bool(user_roles & required_set)


def RolePermissionFactory(roles: Iterable[str], require_all: bool = False, allow_staff: bool = True):
    """
    Dynamically create a permission class tied to a fixed set of roles.

    Example:
        permission_classes = [RolePermissionFactory(["admin", "editor"])]
    """
    class _RolePermission(RolePermission):
        def _get_required_roles(self, view):
            return list(roles)

    _RolePermission.require_all_roles = require_all
    _RolePermission.allow_staff = allow_staff
    return _RolePermission
