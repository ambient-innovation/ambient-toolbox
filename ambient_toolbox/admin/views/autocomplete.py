from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.auth import get_user_model

from ambient_toolbox.admin.utils import get_user_display_label


class UserLabelAutocompleteJsonView(AutocompleteJsonView):
    """
    Custom autocomplete view that displays User objects with full name and email.

    Wire this view into your URL configuration **before** the admin URLs.
    Wrap with ``admin.site.admin_view()`` to enforce staff/login checks::

        from ambient_toolbox.admin.views.autocomplete import UserLabelAutocompleteJsonView

        urlpatterns = [
            path(
                "admin/autocomplete/",
                admin.site.admin_view(UserLabelAutocompleteJsonView.as_view(admin_site=admin.site)),
                name="admin-user-autocomplete",
            ),
            path("admin/", admin.site.urls),
        ]

    Override ``get_user_display_text(user)`` to customise the label format.
    """

    def get_user_display_text(self, user) -> str:
        """Return the display text for a User in autocomplete results. Override to customise."""
        return get_user_display_label(user)

    def serialize_result(self, obj, to_field_name):
        result = super().serialize_result(obj, to_field_name)
        if isinstance(obj, get_user_model()):
            result["text"] = self.get_user_display_text(obj)
        return result
