from django.core import checks
from django.test import SimpleTestCase

from ambient_toolbox.system_checks.model_relation_conventions import check_model_related_names_for_related_name
from testapp.models import ModelWithoutRelatedNameOnFieldAndMeta


class CheckModelRelationConventionsTestCase(SimpleTestCase):
    def test_check_model_related_names_for_related_name_regular(self):
        # Create expected warning
        relation_warning = checks.Warning(
            "'ModelWithoutRelatedNameOnFieldAndMeta.relation_field' doesn't have a related name set and neither "
            "does the model define a default related name.",
            obj=ModelWithoutRelatedNameOnFieldAndMeta.relation_field.field,
            id="ambient_toolbox.W003",
        )

        # Call system check
        error_list = check_model_related_names_for_related_name()

        # Assert warngins
        self.assertEqual(len(error_list), 1)
        self.assertIn(relation_warning, error_list)
