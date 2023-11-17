from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class DjangoPermissionRequiredMixin:
    """
    View mixin to enforce logged-in state and Django permissions.
    """

    permission_list = None
    login_required = True
    login_view_name = "login-view"

    def __init__(self):
        super().__init__()

        if self.permission_list is None:
            raise RuntimeError(
                _("Class-based view using DjangoPermissionRequiredMixin without defining a permission list.")
            )

    def get_login_url(self) -> str:
        """
        Method that can be overwritten to define the login url. If a user has to be logged in but is not, he/she
        will be forwarded to the login view.
        """
        return reverse(self.login_view_name)

    def passes_login_barrier(self, user) -> bool:
        """
        If user does not have to be logged in, we just let anybody pass. Otherwise, user has to be logged in.
        """
        if not self.login_required or user.is_authenticated:
            return True

        return False

    def has_permissions(self, user: User) -> bool:
        # Check every permission...
        for permission in self.permission_list:
            # If user is missing one, the user is not allowed to see the view
            if not user.has_perm(permission):
                return False

        # If all permissions validate, the user can access the view
        return True

    def dispatch(self, request, *args, **kwargs):
        # Validate user is either logged in or doesn't have to be logged in
        if not self.passes_login_barrier(request.user):
            return redirect(self.get_login_url())

        # Validate that user has all required permissions
        if not self.has_permissions(request.user):
            return render(request, "403.html", status=403)

        # If everything goes well, we'll continue to the view
        return super().dispatch(request, *args, **kwargs)
