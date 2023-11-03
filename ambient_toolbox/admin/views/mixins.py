from django.contrib import admin
from django.core.exceptions import PermissionDenied


class AdminViewMixin:
    """
    Mixin to provide a custom view with all the attributes it needs to look like a regular django admin page.
    """

    model = None
    admin_page_title = ""

    def has_view_permission(self, user, **kwargs) -> bool:
        """
        Custom admin views are prone to be left open for all users.
        This method is called in the `dispatch()` and ensures the user has the required permissions to access
        this view. Defaults to the `is_superuser` flag of the django user.
        Can be overwritten if a different permission logic is required.
        """
        return user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        """
        Runs a custom validation to ensure user has the permissions to access this page before running the default
        dispatch logic.
        """
        if self.has_view_permission(request.user):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def get_admin_site(self):
        """
        Returns the set admin site. Can be overwritten if needed.
        """
        return admin.site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin_site = self.get_admin_site()
        context.update(
            {
                "site_header": admin_site.site_header,
                "site_title": admin_site.site_title,
                "title": self.admin_page_title,
                "name": self.admin_page_title,
                "original": self.admin_page_title,
                "is_nav_sidebar_enabled": True,
                "available_apps": admin.site.get_app_list(self.request),
                "opts": {
                    "app_label": self.model._meta.app_label,
                    "verbose_name": self.model._meta.verbose_name,
                    "verbose_name_plural": self.model._meta.verbose_name_plural,
                    "model_name": self.model._meta.model_name,
                    "app_config": {
                        "verbose_name": self.model._meta.app_config.verbose_name,
                    },
                },
                "has_permission": admin_site.has_permission(request=self.request),
            }
        )
        return context
