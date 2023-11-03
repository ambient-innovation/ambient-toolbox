from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.utils.translation import gettext_lazy as _


class CrispyLayoutFormMixin:
    """
    Styles the form in bootstrap style
    """

    def __init__(self, *args, **kwargs):
        # Crispy
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal form-bordered form-row-stripped"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit_button", _("Save")))
        self.helper.form_tag = True
        self.helper.label_class = "col-md-3"
        self.helper.field_class = "col-md-9"
        self.helper.label_size = " col-md-offset-3"

        super().__init__(*args, **kwargs)
