from django.contrib import admin


class ReadOnlyAdmin(admin.ModelAdmin):
    """
    Class for being extended by ModelAdmin-classes.
    Disables all create, delete or edit functionality in the regular admin.
    """

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.readonly_fields = [field.name for field in self.opts.local_fields] + [
                field.name for field in self.opts.local_many_to_many
            ]
        return self.readonly_fields

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = False
        return super().changeform_view(request, object_id, extra_context=extra_context)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class EditableOnlyAdmin(admin.ModelAdmin):
    """
    Class for being extended by ModelAdmin-classes.
    Disables all create and delete functionality so all records can only be edited.
    """

    def get_actions(self, request):
        # Disable delete
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
