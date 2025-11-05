import warnings
from unittest import mock

import pytest
from django.db import models
from django.test import TestCase

from ambient_toolbox.mixins.bleacher import BleacherMixin
from testapp.models import BleacherMixinModel


class BleacherMixinTest(TestCase):
    """Test suite for BleacherMixin."""

    @pytest.mark.filterwarnings("error:Please use a set instead of a list or tuple")
    def test_default_settings_without_warning(self, *args):
        """Test that default settings don't trigger deprecation warnings."""
        BleacherMixinModel()

    @mock.patch.object(BleacherMixin, "DEFAULT_ALLOWED_TAGS", ["a", "b", "p"])
    @pytest.mark.filterwarnings("ignore:Please use a set instead of a list or tuple")
    def test_init_allowed_tags_casted_to_set(self, *args):
        """Test that ALLOWED_TAGS are properly converted to a set."""
        obj = BleacherMixinModel()
        self.assertEqual({"a", "b", "p"}, obj.allowed_tags)
        self.assertIs(True, isinstance(obj.allowed_tags, set))

    @mock.patch.object(BleacherMixin, "DEFAULT_ALLOWED_ATTRIBUTES", {"img": {"alt"}})
    def test_init_allowed_attributes_casted_to_set(self):
        """Test that ALLOWED_ATTRIBUTES values are properly stored as sets."""
        obj = BleacherMixinModel()
        self.assertEqual({"img": {"alt"}}, obj.allowed_attributes)
        self.assertIs(True, isinstance(obj.allowed_attributes["img"], set))

    def test_init_allowed_attributes_list_converted_to_set(self):
        """Test that list attributes are converted to sets with deprecation warning."""

        class BleacherTestModel1(BleacherMixin, models.Model):  # noqa: DJ008
            BLEACH_FIELD_LIST = ["content"]
            ALLOWED_ATTRIBUTES = {"img": ["alt", "src"]}
            content = models.CharField(max_length=50)

            class Meta:
                app_label = "testapp"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            obj = BleacherTestModel1()
            # Verify warning was raised
            self.assertEqual(len(w), 1)
            self.assertIn("Please use a set instead of a list or tuple", str(w[0].message))
            self.assertEqual(w[0].category, DeprecationWarning)
            # Verify conversion happened
            self.assertEqual({"alt", "src"}, obj.allowed_attributes["img"])
            self.assertIsInstance(obj.allowed_attributes["img"], set)

    def test_init_allowed_attributes_tuple_converted_to_set(self):
        """Test that tuple attributes are converted to sets with deprecation warning."""

        class BleacherTestModel2(BleacherMixin, models.Model):  # noqa: DJ008
            BLEACH_FIELD_LIST = ["content"]
            ALLOWED_ATTRIBUTES = {"a": ("href", "rel")}
            content = models.CharField(max_length=50)

            class Meta:
                app_label = "testapp"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            obj = BleacherTestModel2()
            # Verify warning was raised
            self.assertEqual(len(w), 1)
            self.assertIn("Please use a set instead of a list or tuple", str(w[0].message))
            self.assertEqual(w[0].category, DeprecationWarning)
            # Verify conversion happened
            self.assertEqual({"href", "rel"}, obj.allowed_attributes["a"])
            self.assertIsInstance(obj.allowed_attributes["a"], set)

    def test_init_custom_allowed_tags(self):
        """Test initialization with custom ALLOWED_TAGS on model."""

        class BleacherTestModel3(BleacherMixin, models.Model):  # noqa: DJ008
            BLEACH_FIELD_LIST = ["content"]
            ALLOWED_TAGS = ["custom", "special"]
            content = models.CharField(max_length=50)

            class Meta:
                app_label = "testapp"

        obj = BleacherTestModel3()
        self.assertEqual({"custom", "special"}, obj.allowed_tags)

    def test_init_custom_allowed_attributes(self):
        """Test initialization with custom ALLOWED_ATTRIBUTES on model."""

        class BleacherTestModel4(BleacherMixin, models.Model):  # noqa: DJ008
            BLEACH_FIELD_LIST = ["content"]
            ALLOWED_ATTRIBUTES = {"div": {"class", "id"}}
            content = models.CharField(max_length=50)

            class Meta:
                app_label = "testapp"

        obj = BleacherTestModel4()
        self.assertEqual({"div": {"class", "id"}}, obj.allowed_attributes)

    def test_bleach_field_with_empty_string(self):
        """Test that empty fields are not processed."""
        obj = BleacherMixinModel.objects.create(content="")
        self.assertEqual("", obj.content)

    def test_bleach_field_with_none(self):
        """Test that None fields are handled gracefully."""
        obj = BleacherMixinModel(content="<p>Test</p>")
        # Simulate a None field value
        obj.content = None
        obj._bleach_field("content")
        # Should remain None since getattr returns None
        self.assertIsNone(obj.content)

    def test_save_allowed_tag(self):
        """Test that allowed tags are preserved."""
        obj = BleacherMixinModel.objects.create(content="<p>Test</p>")
        self.assertEqual("<p>Test</p>", obj.content)

    def test_save_remove_tags_with_adjacent_content(self):
        """Test that disallowed tags are removed but content is preserved."""
        obj = BleacherMixinModel.objects.create(content="<script>Evil</script>Test")
        self.assertEqual("Test", obj.content)

    def test_save_default_rel_behaviour(self):
        """Test default rel attribute behavior from nh3."""
        obj = BleacherMixinModel.objects.create(content="<a rel='stuff'>Test</a>")
        self.assertEqual('<a rel="noopener noreferrer">Test</a>', obj.content)

    def test_save_tag_removed_content_stays(self):
        """Test that when a tag is removed, its content is preserved."""
        obj = BleacherMixinModel.objects.create(content="<modal>Test</modal>")
        self.assertEqual("Test", obj.content)

    @mock.patch.object(BleacherMixinModel, "DEFAULT_ALLOWED_TAGS", ["modal"])
    def test_save_custom_tag_allowed(self):
        """Test that custom allowed tags work correctly."""
        obj = BleacherMixinModel.objects.create(content="<modal>Test</modal>")
        self.assertEqual("<modal>Test</modal>", obj.content)

    @mock.patch.object(BleacherMixinModel, "DEFAULT_ALLOWED_ATTRIBUTES", {"img": {"alt"}})
    def test_save_custom_attribute_allowed(self):
        """Test that custom allowed attributes work correctly."""
        obj = BleacherMixinModel.objects.create(content='<img alt="Noodle" />')
        self.assertEqual('<img alt="Noodle">', obj.content)

    def test_bleach_multiple_fields(self):
        """Test that multiple fields can be bleached."""

        class MultiFieldModel(BleacherMixin, models.Model):  # noqa: DJ008
            BLEACH_FIELD_LIST = ["field1", "field2"]
            field1 = models.CharField(max_length=50)
            field2 = models.CharField(max_length=50)

            class Meta:
                app_label = "testapp"

        obj = MultiFieldModel(field1="<script>Bad</script>Good1", field2="<script>Bad</script>Good2")
        obj.save = lambda *args, **kwargs: None  # Mock save to just test bleaching
        for field in obj.fields_to_bleach:
            obj._bleach_field(field)

        self.assertEqual("Good1", obj.field1)
        self.assertEqual("Good2", obj.field2)

    def test_init_fields_to_bleach_from_class_attribute(self):
        """Test that BLEACH_FIELD_LIST is properly loaded."""
        obj = BleacherMixinModel()
        self.assertEqual(["content"], obj.fields_to_bleach)
