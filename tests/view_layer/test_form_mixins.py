from django import forms
from django.test import TestCase

from ambient_toolbox.view_layer.form_mixins import CrispyLayoutFormMixin


class DummyForm(forms.Form):
    """Dummy form for testing."""

    name = forms.CharField()


class CrispyLayoutFormWithMixin(CrispyLayoutFormMixin, DummyForm):
    """Form combining CrispyLayoutFormMixin with DummyForm."""


class CrispyLayoutFormMixinTest(TestCase):
    """Test suite for CrispyLayoutFormMixin with 100% branch coverage."""

    def test_initializes_helper_attribute(self):
        """Test that __init__ creates a FormHelper instance."""
        form = CrispyLayoutFormWithMixin()

        self.assertIsNotNone(form.helper)
        self.assertEqual(form.helper.__class__.__name__, "FormHelper")

    def test_sets_form_class_attribute(self):
        """Test that form_class is set to correct Bootstrap classes."""
        form = CrispyLayoutFormWithMixin()

        self.assertEqual(form.helper.form_class, "form-horizontal form-bordered form-row-stripped")

    def test_sets_form_method_attribute(self):
        """Test that form_method is set to 'post'."""
        form = CrispyLayoutFormWithMixin()

        self.assertEqual(form.helper.form_method, "post")

    def test_adds_submit_button(self):
        """Test that a submit button is added to the form."""
        form = CrispyLayoutFormWithMixin()

        self.assertEqual(len(form.helper.inputs), 1)
        submit_button = form.helper.inputs[0]
        self.assertEqual(submit_button.field_classes, "btn btn-primary")
        # The button should have name "submit_button"
        self.assertEqual(submit_button.name, "submit_button")

    def test_submit_button_has_correct_label(self):
        """Test that submit button has 'Save' label (translated)."""
        form = CrispyLayoutFormWithMixin()

        submit_button = form.helper.inputs[0]
        # The value should be a lazy translation object for "Save"
        # We check the string representation
        self.assertEqual(str(submit_button.value), "Save")

    def test_sets_form_tag_attribute(self):
        """Test that form_tag is set to True."""
        form = CrispyLayoutFormWithMixin()

        self.assertTrue(form.helper.form_tag)

    def test_sets_label_class_attribute(self):
        """Test that label_class is set to 'col-md-3'."""
        form = CrispyLayoutFormWithMixin()

        self.assertEqual(form.helper.label_class, "col-md-3")

    def test_sets_field_class_attribute(self):
        """Test that field_class is set to 'col-md-9'."""
        form = CrispyLayoutFormWithMixin()

        self.assertEqual(form.helper.field_class, "col-md-9")

    def test_sets_label_size_attribute(self):
        """Test that label_size is set to ' col-md-offset-3'."""
        form = CrispyLayoutFormWithMixin()

        self.assertEqual(form.helper.label_size, " col-md-offset-3")

    def test_calls_super_init(self):
        """Test that super().__init__() is called to initialize parent classes."""
        # Create the form and verify parent initialization was successful
        form = CrispyLayoutFormWithMixin()

        # Verify that parent __init__ was called by checking form fields are initialized
        self.assertIn("name", form.fields)
        # Verify the field is properly initialized with Django form attributes
        self.assertIsInstance(form.fields["name"], forms.CharField)

    def test_accepts_args_and_kwargs(self):
        """Test that mixin properly passes args and kwargs to parent."""
        data = {"name": "Test Name"}
        form = CrispyLayoutFormWithMixin(data=data)

        # Verify form works correctly with passed data
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Test Name")

    def test_multiple_instantiation(self):
        """Test that multiple form instances have independent helpers."""
        form1 = CrispyLayoutFormWithMixin()
        form2 = CrispyLayoutFormWithMixin()

        # Verify each has its own helper instance
        self.assertIsNot(form1.helper, form2.helper)

    def test_form_renders_with_crispy_helper(self):
        """Test that form can be rendered with crispy helper."""
        form = CrispyLayoutFormWithMixin()

        # Should not raise an exception
        form_html = str(form)
        self.assertIsInstance(form_html, str)
