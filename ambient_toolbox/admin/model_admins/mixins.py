from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.http import HttpResponseRedirect
from django.urls import resolve, reverse


class AdminCreateFormMixin:
    """
    Mixin to easily use a different form for the create case (in comparison to "edit") in the django admin
    Logic copied from `django.contrib.auth.admin.UserAdmin`
    """

    add_form = None

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)


class AdminNoInlinesForCreateMixin:
    """
    Avoid showing any inline admins when being in the create case of a record
    """

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)


class AdminRequestInFormMixin:
    """
    Mixin to add the current request to a form used in the django admin
    """

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form


class FetchParentObjectInlineMixin:
    """
    Fetches the parent object via the URL resolver and makes it available throughout the entire class.
    Attention: Use only in inline admin classes.
    """

    parent_object = None

    @staticmethod
    def _resolve_url(request):
        return resolve(request.path_info)

    def get_parent_object_from_request(self, request):
        resolved = self._resolve_url(request)
        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs.get("object_id", None))
        return None

    def get_formset(self, request, obj=None, **kwargs):
        # Fetch parent object - cannot be done in the init method because request is not available there
        self.parent_object = self.get_parent_object_from_request(request)
        return super().get_formset(request, obj, **kwargs)


class FetchObjectMixin:
    """
    Fetches the current object via the URL resolver and makes it available throughout the entire class.
    """

    def get_object_from_request(self, request):
        resolved = resolve(request.path_info)
        if resolved.kwargs:
            return self.model.objects.get(pk=resolved.kwargs.get("object_id", None))
        return None


class CommonInfoAdminMixin:
    """
    Mixin to be used in a django model admin class.
    Sets all four `CommonInfo` attributes to "readonly" and sets the creator / last modifier on form save.
    """

    def get_readonly_fields(self, request, obj=None):
        """
        Set the fields CommonInfo handles to readonly to avoid users fiddling around with them.
        """
        return super().get_readonly_fields(request, obj) + (
            "created_by",
            "lastmodified_by",
            "created_at",
            "lastmodified_at",
        )

    def get_user_obj(self, request) -> Optional[AbstractUser]:
        """
        Fetches the user object from the current request.
        Can be overwritten when a different user object is required.
        """
        return request.user

    def save_form(self, request, form, change):
        if form.instance and request.user:
            if not form.instance.pk:
                form.instance.created_by = self.get_user_obj(request=request)
            form.instance.lastmodified_by = self.get_user_obj(request=request)

        return super().save_form(request, form, change)


class DeactivatableChangeViewAdminMixin:
    """
    Mixin to be used in model admins to disable the detail page / change view.
    """

    enable_change_view = True

    def can_see_change_view(self, request) -> bool:
        """
        This method determines if the change view is disabled or visible.
        """
        return self.enable_change_view

    def get_list_display_links(self, request, list_display):
        """
        When we don't want to show the change view, there is no need for having a link to it
        """
        if not self.can_see_change_view(request=request):
            return None
        return super().get_list_display_links(request, list_display)

    def change_view(self, request, *args, **kwargs):
        """
        The 'change' admin view for this model.

        We override this to redirect back to the changelist unless the view is
        specifically enabled by the "enable_change_view" property.
        """
        if self.can_see_change_view(request=request):
            return super().change_view(request, *args, **kwargs)
        else:
            opts = self.model._meta
            url = reverse(
                "admin:{app}_{model}_changelist".format(
                    app=opts.app_label,
                    model=opts.model_name,
                )
            )
            return HttpResponseRedirect(url)
