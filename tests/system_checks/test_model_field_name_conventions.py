from django.core import checks
from django.test import SimpleTestCase, override_settings

from ambient_toolbox.system_checks.model_field_name_conventions import check_model_time_based_fields
from testapp.models import ModelNameTimeBasedFieldTest


class CheckModelTimeBasedFieldsTest(SimpleTestCase):
    def test_check_regular(self):
        # Create expected warnings
        datetime_warning = checks.Warning(
            "DateTimeField 'ModelNameTimeBasedFieldTest.wrongly_named_datetime_field' doesn't end with: _at.",
            obj=ModelNameTimeBasedFieldTest.wrongly_named_datetime_field.field,
            id="ambient_toolbox.W001",
        )
        date_warning = checks.Warning(
            "DateField 'ModelNameTimeBasedFieldTest.wrongly_named_date_field' doesn't end with: _date.",
            obj=ModelNameTimeBasedFieldTest.wrongly_named_date_field.field,
            id="ambient_toolbox.W002",
        )

        # Call system check
        error_list = check_model_time_based_fields()

        # Assert warngins
        self.assertEqual(len(error_list), 2)
        self.assertIn(datetime_warning, error_list)
        self.assertIn(date_warning, error_list)

    @override_settings(ALLOWED_MODEL_DATETIME_FIELD_ENDINGS=["wrongly_named_datetime_field", "_at"])
    def test_check_allowlist_works_datetime_field(self):
        # Call system check
        error_list = check_model_time_based_fields()

        # Assert warngins
        self.assertEqual(len(error_list), 1)
        self.assertEqual(error_list[0].id, "ambient_toolbox.W002")

    @override_settings(ALLOWED_MODEL_DATE_FIELD_ENDINGS=["wrongly_named_date_field", "_date"])
    def test_check_allowlist_works_date_field(self):
        # Call system check
        error_list = check_model_time_based_fields()

        # Assert warngins
        self.assertEqual(len(error_list), 1)
        self.assertEqual(error_list[0].id, "ambient_toolbox.W001")
