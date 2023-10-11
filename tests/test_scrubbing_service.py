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

    # todo write more tests
