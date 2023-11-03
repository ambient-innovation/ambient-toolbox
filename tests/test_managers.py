from django.contrib.auth.models import User
from django.test import TestCase

from testapp.models import MySingleSignalModel


class GloballyVisibleQuerySetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Create test user
        cls.user = User.objects.create(username="my-username")

        # Create list of objects
        cls.object_list = [
            MySingleSignalModel.objects.create(value=1),
            MySingleSignalModel.objects.create(value=2),
        ]

    def test_visible_for_regular(self):
        self.assertGreater(len(self.object_list), 0)
        self.assertEqual(MySingleSignalModel.objects.visible_for(self.user).count(), len(self.object_list))

    def test_editable_for_regular(self):
        self.assertGreater(len(self.object_list), 0)
        self.assertEqual(MySingleSignalModel.objects.editable_for(self.user).count(), len(self.object_list))

    def test_deletable_for_regular(self):
        self.assertGreater(len(self.object_list), 0)
        self.assertEqual(MySingleSignalModel.objects.deletable_for(self.user).count(), len(self.object_list))
