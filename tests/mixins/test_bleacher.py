from unittest import mock

import pytest
from django.test import TestCase

from ambient_toolbox.mixins.bleacher import BleacherMixin
from testapp.models import BleacherMixinModel


class BleacherMixinTest(TestCase):
    @pytest.mark.filterwarnings("error:Please use a set instead of a list or tuple")
    def test_default_settings_without_warning(self, *args):
        # ensure there are no deprecation warnings with default settings
        BleacherMixinModel()

    @mock.patch.object(BleacherMixin, "DEFAULT_ALLOWED_TAGS", ["a", "b", "p"])
    @pytest.mark.filterwarnings("ignore:Please use a set instead of a list or tuple")
    def test_init_allowed_tags_casted_to_set(self, *args):
        obj = BleacherMixinModel()
        self.assertEqual({"a", "b", "p"}, obj.allowed_tags)
        self.assertIs(True, isinstance(obj.allowed_tags, set))

    @mock.patch.object(BleacherMixin, "DEFAULT_ALLOWED_ATTRIBUTES", {"img": {"alt"}})
    def test_init_allowed_attributes_casted_to_set(self):
        obj = BleacherMixinModel()
        self.assertEqual({"img": {"alt"}}, obj.allowed_attributes)
        self.assertIs(True, isinstance(obj.allowed_attributes["img"], set))

    def test_save_allowed_tag(self):
        obj = BleacherMixinModel.objects.create(content="<p>Test</p>")
        self.assertEqual("<p>Test</p>", obj.content)

    def test_save_remove_tags_with_adjacent_content(self):
        obj = BleacherMixinModel.objects.create(content="<script>Evil</script>Test")
        self.assertEqual("Test", obj.content)

    def test_save_default_rel_behaviour(self):
        obj = BleacherMixinModel.objects.create(content="<a rel='stuff'>Test</a>")
        self.assertEqual('<a rel="noopener noreferrer">Test</a>', obj.content)

    def test_save_tag_removed_content_stays(self):
        obj = BleacherMixinModel.objects.create(content="<modal>Test</modal>")
        self.assertEqual("Test", obj.content)

    @mock.patch.object(BleacherMixinModel, "DEFAULT_ALLOWED_TAGS", ["modal"])
    def test_save_custom_tag_allowed(self):
        obj = BleacherMixinModel.objects.create(content="<modal>Test</modal>")
        self.assertEqual("<modal>Test</modal>", obj.content)

    @mock.patch.object(BleacherMixinModel, "DEFAULT_ALLOWED_ATTRIBUTES", {"img": {"alt"}})
    def test_save_custom_attribute_allowed(self):
        obj = BleacherMixinModel.objects.create(content='<img alt="Noodle" />')
        self.assertEqual('<img alt="Noodle">', obj.content)
