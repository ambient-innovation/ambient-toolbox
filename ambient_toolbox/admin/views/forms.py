from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Fieldset, Layout, Submit
from django import forms
from django.utils.translation import gettext_lazy as _


class AdminCrispyForm(forms.Form):
    """
    Base crispy form to be used in custom views within the django admin.
    """

    section_title = _("No title defined")
    button_label = _("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Build fieldset
        fieldset_list = [""]
        for field in self.fields:
            fieldset_list.append(Div(field, css_class="form-row field-name"))  # noqa: PERF401

        # Crispy
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", self.button_label, css_class="button btn-primary"))
        self.helper.layout = Layout(
            Div(
                Div(HTML(f"<h2>{self.section_title}</h2>"), Fieldset(*fieldset_list), css_class="module aligned"),
                css_class="custom-form",
            ),
        )
