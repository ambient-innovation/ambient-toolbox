from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from ambient_toolbox.validators.auth_password.special_chars import SpecialCharValidator


class SpecialCharValidatorTest(TestCase):
    def test_validate_happy_path(self):
        validator = SpecialCharValidator()
        self.assertIsNone(validator.validate("Admin0404!"))

    def test_validate_missing_special_char(self):
        validator = SpecialCharValidator()
        with self.assertRaisesMessage(
            ValidationError, 'The password has to contain one of the following special characters: "@#$%!^&*"'
        ):
            validator.validate("EasyPassword")

    def test_get_help_text_regular(self):
        validator = SpecialCharValidator()
        self.assertEqual(
            validator.get_help_text(), 'The password has to contain one of the following special characters: "@#$%!^&*"'
        )

    @override_settings(AUTH_PASSWORD_VALIDATORS=["ambient_toolbox.validators.SpecialCharValidator"])
    def test_functional_happy_path(self):
        user = User()
        self.assertIsNone(user.set_password("Admin0404!"))

    @override_settings(AUTH_PASSWORD_VALIDATORS=["ambient_toolbox.validators.auth_password.SpecialCharValidator"])
    def test_functional_special_char_missing(self):
        user = User()
        self.assertFalse(user.set_password("EasyPassword"))
