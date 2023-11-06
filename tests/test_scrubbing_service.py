from unittest import mock

from django.test import TestCase, override_settings

from ambient_toolbox.services.custom_scrubber import AbstractScrubbingService, ScrubbingError


class AbstractScrubbingServiceTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.service = AbstractScrubbingService()

    @override_settings(DEBUG=False)
    def test_scrubber_debug_mode_needs_to_be_active(self):
        with self.assertRaisesMessage(ScrubbingError, "Scrubber settings validation failed"):
            self.service.process()

    @override_settings(DEBUG=True, INSTALLED_APPS=[])
    def test_scrubber_needs_to_be_installed(self):
        with self.assertRaisesMessage(ScrubbingError, "Scrubber settings validation failed"):
            self.service.process()

    @mock.patch("ambient_toolbox.services.custom_scrubber.make_password")
    def test_get_hashed_default_password_regular(self, mocked_make_password):
        self.service._get_hashed_default_password()
        mocked_make_password.assert_called_once_with(self.service.DEFAULT_USER_PASSWORD)

    # TODO: write more tests
