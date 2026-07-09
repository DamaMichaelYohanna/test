from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect

class BasePermissionMixin(UserPassesTestMixin):
    permission_denied_message = "You do not have permission to access this page."
    redirect_url = 'projects:project_list'

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect(self.redirect_url)

class Level2RequiredMixin(BasePermissionMixin):
    """Requires user to be a Superuser or belong to Level 2, Level 3, or Level 4 groups."""
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return (
            user.is_superuser or 
            user.groups.filter(name__in=['Level 2', 'Level 3', 'Level 4']).exists()
        )

class Level3RequiredMixin(BasePermissionMixin):
    """Requires user to be a Superuser or belong to Level 3 or Level 4 groups."""
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return (
            user.is_superuser or 
            user.groups.filter(name__in=['Level 3', 'Level 4']).exists()
        )

class Level4RequiredMixin(BasePermissionMixin):
    """Requires user to be a Superuser or belong to Level 4 group."""
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return (
            user.is_superuser or 
            user.groups.filter(name__in=['Level 4']).exists()
        )
