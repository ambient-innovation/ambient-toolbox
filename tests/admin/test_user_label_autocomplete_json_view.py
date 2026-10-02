from unittest import mock

from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.auth.models import User
from django.test import TestCase

from ambient_toolbox.admin.views.autocomplete import UserLabelAutocompleteJsonView


class UserLabelAutocompleteJsonViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = User.objects.create(username="my_user", first_name="Jane", last_name="Doe", email="jane@example.com")

    def _get_view(self):
        return UserLabelAutocompleteJsonView()

    def test_serialize_result_overrides_text_for_user(self):
        view = self._get_view()
        with mock.patch.object(
            AutocompleteJsonView,
            "serialize_result",
            return_value={"id": str(self.user.pk), "text": str(self.user)},
        ):
            result = view.serialize_result(self.user, "pk")

        self.assertEqual(result["text"], "Jane Doe (jane@example.com)")

    def test_serialize_result_does_not_override_for_non_user(self):
        view = self._get_view()
        non_user = mock.Mock(spec=[])
        non_user.pk = 1

        with mock.patch.object(
            AutocompleteJsonView,
            "serialize_result",
            return_value={"id": "1", "text": "Original Text"},
        ):
            result = view.serialize_result(non_user, "pk")

        self.assertEqual(result["text"], "Original Text")

    def test_get_user_display_text_default(self):
        view = self._get_view()
        text = view.get_user_display_text(self.user)
        self.assertEqual(text, "Jane Doe (jane@example.com)")

    def test_get_user_display_text_can_be_overridden(self):
        class CustomView(UserLabelAutocompleteJsonView):
            def get_user_display_text(self, user) -> str:
                return f"Custom: {user.email}"

        view = CustomView()
        with mock.patch.object(
            AutocompleteJsonView,
            "serialize_result",
            return_value={"id": str(self.user.pk), "text": str(self.user)},
        ):
            result = view.serialize_result(self.user, "pk")

        self.assertEqual(result["text"], "Custom: jane@example.com")
