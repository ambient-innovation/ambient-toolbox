from django.test import TestCase

from ambient_toolbox.utils import object_to_dict
from testapp.models import ForeignKeyRelatedModel, MySingleSignalModel


class UtilModelTest(TestCase):
    def test_object_to_dict_regular(self):
        obj = MySingleSignalModel.objects.create(value=17)
        self.assertEqual(object_to_dict(obj), {"value": obj.value})

    def test_object_to_dict_blacklist(self):
        obj = MySingleSignalModel.objects.create(value=17)
        self.assertEqual(object_to_dict(obj, ["value"]), {})

    def test_object_to_dict_with_id_with_blacklist(self):
        obj = MySingleSignalModel.objects.create(value=17)
        self.assertEqual(object_to_dict(obj, ["value"], True), {"id": obj.id})

    def test_with_id_no_blacklist(self):
        obj = MySingleSignalModel.objects.create(value=17)
        self.assertEqual(object_to_dict(obj, include_id=True), {"id": obj.id, "value": obj.value})

    def test_object_to_dict_valid_fields_append(self):
        obj = MySingleSignalModel.objects.create(value=17)
        dummy_instance = ForeignKeyRelatedModel(single_signal=obj)

        valid_data = object_to_dict(dummy_instance)

        self.assertIn("single_signal_id", valid_data)
        self.assertEqual(valid_data["single_signal_id"], obj.id)
