from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.test import TestCase

from ambient_toolbox.admin.views.forms import AdminCrispyForm


class AdminFormTest(TestCase):
    def test_admin_crispy_form_regular(self):
        # Form provides mostly styling, so we just validate that it renders
        form = AdminCrispyForm()

        self.assertIsInstance(form.helper, FormHelper)
        self.assertIsInstance(form.helper.layout, Layout)
        self.assertEqual(form.helper.form_method, 'post')
