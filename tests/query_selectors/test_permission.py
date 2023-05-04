from django.test import TestCase

from ambient_toolbox.selectors.permission import AbstractUserSpecificSelectorMixin
from testapp.models import ModelWithSelector


class AbstractUserSpecificSelectorMixinTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.mixin = AbstractUserSpecificSelectorMixin()

    def test_visible_for_method_available(self):
        with self.assertRaises(NotImplementedError):
            self.mixin.visible_for(user_id=-1)

    def test_editable_for_method_available(self):
        with self.assertRaises(NotImplementedError):
            self.mixin.editable_for(user_id=-1)

    def test_deletable_for_method_available(self):
        with self.assertRaises(NotImplementedError):
            self.mixin.deletable_for(user_id=-1)


class GloballyVisibleSelectorMixinTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.obj = ModelWithSelector.objects.create(value=1)

    def test_visible_for_method_available(self):
        qs = ModelWithSelector.selectors.visible_for(user_id=-1)

        self.assertEqual(qs.count(), 1)
        self.assertIn(self.obj, qs)

    def test_editable_for_method_available(self):
        qs = ModelWithSelector.selectors.editable_for(user_id=-1)

        self.assertEqual(qs.count(), 1)
        self.assertIn(self.obj, qs)

    def test_deletable_for_method_available(self):
        qs = ModelWithSelector.selectors.deletable_for(user_id=-1)

        self.assertEqual(qs.count(), 1)
        self.assertIn(self.obj, qs)
