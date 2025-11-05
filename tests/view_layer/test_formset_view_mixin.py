from unittest import mock

from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.test import RequestFactory, TestCase
from django.views import generic

from ambient_toolbox.tests.mixins import RequestProviderMixin
from ambient_toolbox.view_layer.formset_view_mixin import (
    FormsetCreateViewMixin,
    FormsetUpdateViewMixin,
    _FormsetMixin,
)
from testapp.models import ForeignKeyRelatedModel, MySingleSignalModel


class MySingleSignalModelForm(forms.ModelForm):
    """Form for MySingleSignalModel."""

    class Meta:
        model = MySingleSignalModel
        fields = ("value",)


class ForeignKeyRelatedModelForm(forms.ModelForm):
    """Form for ForeignKeyRelatedModel."""

    class Meta:
        model = ForeignKeyRelatedModel
        fields = ("single_signal",)


class FormsetMixinTest(RequestProviderMixin, TestCase):
    """Test suite for _FormsetMixin."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_model = MySingleSignalModel.objects.create(value=10)
        self.formset_class = inlineformset_factory(
            MySingleSignalModel,
            ForeignKeyRelatedModel,
            form=ForeignKeyRelatedModelForm,
            extra=1,
            can_delete=False,
        )

    class TestUpdateView(_FormsetMixin, generic.UpdateView):
        """Test view that uses _FormsetMixin with UpdateView."""

        model = MySingleSignalModel
        form_class = MySingleSignalModelForm
        template_name = "test_template.html"
        success_url = "/success/"

        def __init__(self):
            super().__init__()
            self.formset_class = inlineformset_factory(
                MySingleSignalModel,
                ForeignKeyRelatedModel,
                form=ForeignKeyRelatedModelForm,
                extra=1,
                can_delete=False,
            )

    def test_get_formset_kwargs_returns_instance(self):
        """Test that get_formset_kwargs() returns dict with instance."""
        view = self.TestUpdateView()
        view.object = self.test_model

        kwargs = view.get_formset_kwargs()

        self.assertIsInstance(kwargs, dict)
        self.assertIn("instance", kwargs)
        self.assertEqual(kwargs["instance"], self.test_model)

    def test_get_formset_kwargs_with_none_object(self):
        """Test that get_formset_kwargs() works with None object."""
        view = self.TestUpdateView()
        view.object = None

        kwargs = view.get_formset_kwargs()

        self.assertIsInstance(kwargs, dict)
        self.assertIn("instance", kwargs)
        self.assertIsNone(kwargs["instance"])

    def test_get_context_data_adds_formset(self):
        """Test that get_context_data() adds formset to context."""
        view = self.TestUpdateView()
        view.object = self.test_model
        view.request = self.get_request()

        context = view.get_context_data()

        self.assertIn("formset", context)
        self.assertIsInstance(context["formset"], BaseInlineFormSet)

    def test_post_with_valid_form_and_formset_calls_form_valid(self):
        """Test that post() calls form_valid() when both form and formset are valid."""
        factory = RequestFactory()
        view = self.TestUpdateView()
        view.object = self.test_model
        view.kwargs = {"pk": self.test_model.pk}

        # Create POST data
        request = factory.post(
            "/",
            data={
                "value": "20",
                "foreignkeyrelatedmodel_set-TOTAL_FORMS": "0",
                "foreignkeyrelatedmodel_set-INITIAL_FORMS": "0",
                "foreignkeyrelatedmodel_set-MIN_NUM_FORMS": "0",
                "foreignkeyrelatedmodel_set-MAX_NUM_FORMS": "1000",
            },
        )
        view.request = request

        # Mock form and formset is_valid to return True
        mock_form = mock.Mock()
        mock_form.is_valid.return_value = True
        mock_formset = mock.Mock()
        mock_formset.is_valid.return_value = True

        with mock.patch.object(view, "get_form_class") as mock_get_form_class:
            mock_get_form_class.return_value = mock.Mock(return_value=mock_form)
            with mock.patch.object(view, "formset_class", return_value=mock_formset):
                with mock.patch.object(view, "form_valid") as mock_form_valid:
                    mock_form_valid.return_value = mock.Mock(status_code=302)
                    view.post(request)
                    mock_form_valid.assert_called_once()

    @mock.patch("ambient_toolbox.view_layer.formset_view_mixin.render")
    def test_post_with_invalid_form_renders_template(self, mock_render):
        """Test that post() renders template when form is invalid."""
        factory = RequestFactory()
        view = self.TestUpdateView()
        view.object = self.test_model
        view.kwargs = {"pk": self.test_model.pk}

        # Create invalid POST data (missing required field)
        request = factory.post(
            "/",
            data={
                "foreignkeyrelatedmodel_set-TOTAL_FORMS": "1",
                "foreignkeyrelatedmodel_set-INITIAL_FORMS": "0",
                "foreignkeyrelatedmodel_set-MIN_NUM_FORMS": "0",
                "foreignkeyrelatedmodel_set-MAX_NUM_FORMS": "1000",
            },
        )
        view.request = request

        mock_render.return_value = mock.Mock(status_code=200)
        view.post(request)

        mock_render.assert_called_once()
        call_args = mock_render.call_args
        self.assertEqual(call_args[0][0], request)
        self.assertIn("form", call_args[0][2])
        self.assertIn("formset", call_args[0][2])

    @mock.patch("ambient_toolbox.view_layer.formset_view_mixin.render")
    def test_post_with_invalid_formset_renders_template(self, mock_render):
        """Test that post() renders template when formset is invalid."""
        factory = RequestFactory()
        view = self.TestUpdateView()
        view.object = self.test_model
        view.kwargs = {"pk": self.test_model.pk}

        # Create invalid POST data (invalid formset data)
        request = factory.post(
            "/",
            data={
                "value": "20",
                "foreignkeyrelatedmodel_set-TOTAL_FORMS": "1",
                "foreignkeyrelatedmodel_set-INITIAL_FORMS": "0",
                "foreignkeyrelatedmodel_set-MIN_NUM_FORMS": "0",
                "foreignkeyrelatedmodel_set-MAX_NUM_FORMS": "1000",
                "foreignkeyrelatedmodel_set-0-single_signal": "999999",  # Invalid FK
            },
        )
        view.request = request

        mock_render.return_value = mock.Mock(status_code=200)
        view.post(request)

        mock_render.assert_called_once()
        call_args = mock_render.call_args
        self.assertEqual(call_args[0][0], request)
        self.assertIn("form", call_args[0][2])
        self.assertIn("formset", call_args[0][2])

    def test_form_valid_calls_super_and_saves_formset(self):
        """Test that form_valid() calls super().form_valid() and saves formset."""
        view = self.TestUpdateView()
        view.object = self.test_model
        view.request = self.get_request(method="POST")
        view.kwargs = {"pk": self.test_model.pk}

        # Create mock form and formset
        mock_form = mock.Mock()
        mock_form.save.return_value = self.test_model
        mock_formset = mock.Mock()
        mock_formset.instance = self.test_model

        with mock.patch.object(
            generic.UpdateView, "form_valid", return_value=mock.Mock(status_code=302)
        ) as mock_super_form_valid:
            response = view.form_valid(mock_form, mock_formset)
            mock_super_form_valid.assert_called_once_with(form=mock_form)
            mock_formset.save.assert_called_once()
            self.assertEqual(response.status_code, 302)

    def test_form_valid_calls_additional_is_valid_if_exists(self):
        """Test that form_valid() calls additional_is_valid() if it exists."""

        class TestViewWithAdditionalIsValid(self.TestUpdateView):
            """Test view with additional_is_valid method."""

            def __init__(self):
                super().__init__()
                self.additional_is_valid_called = False

            def additional_is_valid(self, form, formset):
                self.additional_is_valid_called = True

        view = TestViewWithAdditionalIsValid()
        view.object = self.test_model
        view.request = self.get_request(method="POST")
        view.kwargs = {"pk": self.test_model.pk}

        # Create mock form and formset
        mock_form = mock.Mock()
        mock_form.save.return_value = self.test_model
        mock_formset = mock.Mock()
        mock_formset.instance = self.test_model

        with mock.patch.object(generic.UpdateView, "form_valid", return_value=mock.Mock(status_code=302)):
            response = view.form_valid(mock_form, mock_formset)

        self.assertTrue(view.additional_is_valid_called)
        self.assertEqual(response.status_code, 302)

    def test_form_valid_does_not_call_additional_is_valid_if_not_exists(self):
        """Test that form_valid() works without additional_is_valid method."""
        view = self.TestUpdateView()
        view.object = self.test_model
        view.request = self.get_request(method="POST")
        view.kwargs = {"pk": self.test_model.pk}

        # Create mock form and formset
        mock_form = mock.Mock()
        mock_form.save.return_value = self.test_model
        mock_formset = mock.Mock()
        mock_formset.instance = self.test_model

        with mock.patch.object(generic.UpdateView, "form_valid", return_value=mock.Mock(status_code=302)):
            # Should not raise AttributeError
            response = view.form_valid(mock_form, mock_formset)
            self.assertEqual(response.status_code, 302)

    def test_form_valid_updates_formset_instance_with_object(self):
        """Test that form_valid() updates formset.instance with self.object."""
        view = self.TestUpdateView()
        view.object = self.test_model
        view.request = self.get_request(method="POST")
        view.kwargs = {"pk": self.test_model.pk}

        # Create mock form and formset
        mock_form = mock.Mock()
        new_object = MySingleSignalModel.objects.create(value=30)
        mock_form.save.return_value = new_object
        mock_formset = mock.Mock()
        mock_formset.instance = self.test_model

        with mock.patch.object(generic.UpdateView, "form_valid", return_value=mock.Mock(status_code=302)):
            # Before form_valid, the formset instance should be test_model
            self.assertEqual(mock_formset.instance, self.test_model)

            view.form_valid(mock_form, mock_formset)

            # After form_valid, formset.instance should be set to view.object
            # (which is updated by super().form_valid())
            self.assertEqual(mock_formset.instance, view.object)

    def test_post_passes_formset_kwargs_to_formset(self):
        """Test that post() passes formset kwargs when creating formset."""
        factory = RequestFactory()
        view = self.TestUpdateView()
        view.object = self.test_model
        view.kwargs = {"pk": self.test_model.pk}

        request = factory.post(
            "/",
            data={
                "value": "20",
                "foreignkeyrelatedmodel_set-TOTAL_FORMS": "0",
                "foreignkeyrelatedmodel_set-INITIAL_FORMS": "0",
                "foreignkeyrelatedmodel_set-MIN_NUM_FORMS": "0",
                "foreignkeyrelatedmodel_set-MAX_NUM_FORMS": "1000",
            },
        )
        view.request = request

        with mock.patch.object(
            view, "get_formset_kwargs", return_value={"instance": self.test_model}
        ) as mock_get_formset_kwargs:
            with mock.patch("ambient_toolbox.view_layer.formset_view_mixin.render") as mock_render:
                mock_render.return_value = mock.Mock(status_code=200)
                view.post(request)
                mock_get_formset_kwargs.assert_called()


class FormsetUpdateViewMixinTest(RequestProviderMixin, TestCase):
    """Test suite for FormsetUpdateViewMixin."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_model = MySingleSignalModel.objects.create(value=10)
        self.formset_class = inlineformset_factory(
            MySingleSignalModel,
            ForeignKeyRelatedModel,
            form=ForeignKeyRelatedModelForm,
            extra=1,
            can_delete=False,
        )

    class TestView(FormsetUpdateViewMixin, generic.UpdateView):
        """Test view that uses FormsetUpdateViewMixin."""

        model = MySingleSignalModel
        form_class = MySingleSignalModelForm
        template_name = "test_template.html"
        success_url = "/success/"

        def __init__(self):
            super().__init__()
            self.formset_class = inlineformset_factory(
                MySingleSignalModel,
                ForeignKeyRelatedModel,
                form=ForeignKeyRelatedModelForm,
                extra=1,
                can_delete=False,
            )

    def test_post_sets_object_from_get_object(self):
        """Test that post() sets self.object from get_object()."""
        factory = RequestFactory()
        view = self.TestView()
        view.kwargs = {"pk": self.test_model.pk}

        request = factory.post(
            "/",
            data={
                "value": "20",
                "foreignkeyrelatedmodel_set-TOTAL_FORMS": "1",
                "foreignkeyrelatedmodel_set-INITIAL_FORMS": "0",
                "foreignkeyrelatedmodel_set-MIN_NUM_FORMS": "0",
                "foreignkeyrelatedmodel_set-MAX_NUM_FORMS": "1000",
            },
        )
        view.request = request

        with mock.patch.object(view, "get_object", return_value=self.test_model) as mock_get_object:
            with mock.patch("ambient_toolbox.view_layer.formset_view_mixin.render") as mock_render:
                mock_render.return_value = mock.Mock(status_code=200)
                view.post(request)
                mock_get_object.assert_called_once()
                self.assertEqual(view.object, self.test_model)

    @mock.patch("ambient_toolbox.view_layer.formset_view_mixin.render")
    def test_post_calls_parent_post(self, mock_render):
        """Test that post() calls parent class post() method."""
        factory = RequestFactory()
        view = self.TestView()
        view.kwargs = {"pk": self.test_model.pk}

        request = factory.post(
            "/",
            data={
                "value": "20",
                "foreignkeyrelatedmodel_set-TOTAL_FORMS": "1",
                "foreignkeyrelatedmodel_set-INITIAL_FORMS": "0",
                "foreignkeyrelatedmodel_set-MIN_NUM_FORMS": "0",
                "foreignkeyrelatedmodel_set-MAX_NUM_FORMS": "1000",
            },
        )
        view.request = request

        mock_render.return_value = mock.Mock(status_code=200)

        # Verify that the parent post() is called by checking that
        # get_form_class and get_form_kwargs are called
        with mock.patch.object(view, "get_form_class", return_value=MySingleSignalModelForm) as mock_get_form_class:
            view.post(request)
            mock_get_form_class.assert_called()


class FormsetCreateViewMixinTest(RequestProviderMixin, TestCase):
    """Test suite for FormsetCreateViewMixin."""

    def setUp(self):
        """Set up test fixtures."""
        self.formset_class = inlineformset_factory(
            MySingleSignalModel,
            ForeignKeyRelatedModel,
            form=ForeignKeyRelatedModelForm,
            extra=1,
            can_delete=False,
        )

    class TestView(FormsetCreateViewMixin, generic.CreateView):
        """Test view that uses FormsetCreateViewMixin."""

        model = MySingleSignalModel
        form_class = MySingleSignalModelForm
        template_name = "test_template.html"
        success_url = "/success/"

        def __init__(self):
            super().__init__()
            self.formset_class = inlineformset_factory(
                MySingleSignalModel,
                ForeignKeyRelatedModel,
                form=ForeignKeyRelatedModelForm,
                extra=1,
                can_delete=False,
            )

    def test_post_sets_object_to_none(self):
        """Test that post() sets self.object to None."""
        factory = RequestFactory()
        view = self.TestView()

        request = factory.post(
            "/",
            data={
                "value": "15",
                "foreignkeyrelatedmodel_set-TOTAL_FORMS": "1",
                "foreignkeyrelatedmodel_set-INITIAL_FORMS": "0",
                "foreignkeyrelatedmodel_set-MIN_NUM_FORMS": "0",
                "foreignkeyrelatedmodel_set-MAX_NUM_FORMS": "1000",
            },
        )
        view.request = request

        with mock.patch("ambient_toolbox.view_layer.formset_view_mixin.render") as mock_render:
            mock_render.return_value = mock.Mock(status_code=200)
            view.post(request)
            self.assertIsNone(view.object)

    @mock.patch("ambient_toolbox.view_layer.formset_view_mixin.render")
    def test_post_calls_parent_post(self, mock_render):
        """Test that post() calls parent class post() method."""
        factory = RequestFactory()
        view = self.TestView()

        request = factory.post(
            "/",
            data={
                "value": "15",
                "foreignkeyrelatedmodel_set-TOTAL_FORMS": "1",
                "foreignkeyrelatedmodel_set-INITIAL_FORMS": "0",
                "foreignkeyrelatedmodel_set-MIN_NUM_FORMS": "0",
                "foreignkeyrelatedmodel_set-MAX_NUM_FORMS": "1000",
            },
        )
        view.request = request

        mock_render.return_value = mock.Mock(status_code=200)

        # Verify that the parent post() is called by checking that
        # get_form_class and get_form_kwargs are called
        with mock.patch.object(view, "get_form_class", return_value=MySingleSignalModelForm) as mock_get_form_class:
            view.post(request)
            mock_get_form_class.assert_called()

    def test_post_with_valid_data_creates_object(self):
        """Test that post() with valid data creates an object."""
        factory = RequestFactory()
        view = self.TestView()

        request = factory.post(
            "/",
            data={
                "value": "15",
                "foreignkeyrelatedmodel_set-TOTAL_FORMS": "0",
                "foreignkeyrelatedmodel_set-INITIAL_FORMS": "0",
                "foreignkeyrelatedmodel_set-MIN_NUM_FORMS": "0",
                "foreignkeyrelatedmodel_set-MAX_NUM_FORMS": "1000",
            },
        )
        view.request = request

        # Mock form and formset is_valid to return True
        mock_form = mock.Mock()
        mock_form.is_valid.return_value = True
        mock_formset = mock.Mock()
        mock_formset.is_valid.return_value = True

        with mock.patch.object(view, "get_form_class") as mock_get_form_class:
            mock_get_form_class.return_value = mock.Mock(return_value=mock_form)
            with mock.patch.object(view, "formset_class", return_value=mock_formset):
                with mock.patch.object(view, "form_valid") as mock_form_valid:
                    mock_form_valid.return_value = mock.Mock(status_code=302)
                    view.post(request)

                    # Verify that a new object would be created in the normal flow
                    # (form_valid was called which would save the object)
                    mock_form_valid.assert_called_once()
