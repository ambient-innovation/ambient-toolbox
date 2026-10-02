from unittest import mock

from django.test import TestCase

from ambient_toolbox.admin.utils import get_user_display_label


class GetUserDisplayLabelTest(TestCase):
    def _make_user(self, first_name="", last_name="", email="", username="testuser"):
        user = mock.Mock()
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.get_full_name.return_value = f"{first_name} {last_name}".strip()
        user.__str__ = mock.Mock(return_value=username)
        return user

    def test_full_name_and_email(self):
        user = self._make_user(first_name="Jane", last_name="Doe", email="jane@example.com")
        self.assertEqual(get_user_display_label(user), "Jane Doe (jane@example.com)")

    def test_first_name_only_with_email(self):
        user = self._make_user(first_name="Jane", email="jane@example.com")
        self.assertEqual(get_user_display_label(user), "Jane (jane@example.com)")

    def test_email_only(self):
        user = self._make_user(email="jane@example.com")
        self.assertEqual(get_user_display_label(user), "jane@example.com")

    def test_full_name_only_no_email(self):
        user = self._make_user(first_name="Jane", last_name="Doe")
        self.assertEqual(get_user_display_label(user), "Jane Doe")

    def test_whitespace_full_name_falls_back_to_email(self):
        user = self._make_user(email="jane@example.com")
        user.get_full_name.return_value = "   "
        self.assertEqual(get_user_display_label(user), "jane@example.com")

    def test_no_name_no_email_falls_back_to_str(self):
        user = self._make_user(username="jdoe42")
        self.assertEqual(get_user_display_label(user), "jdoe42")
