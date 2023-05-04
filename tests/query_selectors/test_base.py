from django.db.models import manager
from django.test import TestCase

from ambient_toolbox.selectors.base import Selector
from testapp.models import ModelWithSelector


class SelectorTest(TestCase):
    def test_selector_inherits_from_django_manager(self):
        base_selector = Selector()
        self.assertIsInstance(base_selector, manager.Manager)

    def test_registering_in_model_is_possible(self):
        self.assertIsInstance(ModelWithSelector.selectors, manager.Manager)
