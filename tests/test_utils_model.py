from django.test import TestCase

from ambient_toolbox.utils import object_to_dict
from testapp.models import MySingleSignalModel


class UtilModelTest(TestCase):
    def test_object_to_dict_regular(self):
        obj = MySingleSignalModel.objects.create(value=17)
        self.assertEqual(object_to_dict(obj), {'value': obj.value})

    def test_object_to_dict_blacklist(self):
        obj = MySingleSignalModel.objects.create(value=17)
        self.assertEqual(object_to_dict(obj, ['value']), {})

    def test_object_to_dict_with_id_with_blacklist(self):
        obj = MySingleSignalModel.objects.create(value=17)
        self.assertEqual(object_to_dict(obj, ['value'], True), {'id': obj.id})

    def test_object_to_dict_with_id_no_blacklist(self):
        obj = MySingleSignalModel.objects.create(value=17)
        self.assertEqual(object_to_dict(obj, include_id=True), {'id': obj.id, 'value': obj.value})
