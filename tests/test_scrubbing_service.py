from django.test import TestCase, override_settings

from ambient_toolbox.services.custom_scrubber import AbstractScrubbingService


class AbstractScrubbingServiceTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.service = AbstractScrubbingService()

    @override_settings(DEBUG=False)
    def test_scrubber_debug_mode_needs_to_be_active(self):
        self.assertEqual(self.service.process(), False)

    @override_settings(DEBUG=True, INSTALLED_APPS=[])
    def test_scrubber_needs_to_be_installed(self):
        self.assertEqual(self.service.process(), False)

    # todo write more tests
