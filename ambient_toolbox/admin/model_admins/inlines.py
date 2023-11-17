from django.contrib import admin


class ReadOnlyTabularInline(admin.TabularInline):
    """
    Class for being extended by TabularInline-classes.
    Disables all create, delete or edit functionality in the tabular inline admin.
    """

    can_delete = False

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False

    def get_readonly_fields(self, request, obj=None):
        result = list(
            set(
                [field.name for field in self.opts.local_fields]
                + [field.name for field in self.opts.local_many_to_many]
            )
        )
        result.remove("id")
        return result
