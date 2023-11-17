class CountChildrenFormsetMixin:
    """
    Provides a method to count the valid children of a formset. Takes care about records which are to be deleted.
    """

    def get_number_of_children(self):
        # Count all choices which are not being deleted right now
        no_choices = 0
        for form in self.forms:
            if getattr(form, "cleaned_data", None) and not form.cleaned_data.get("DELETE"):
                no_choices += 1
        return no_choices
