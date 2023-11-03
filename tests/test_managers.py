from django.contrib.auth.models import User
from django.test import TestCase

from ambient_toolbox.managers import (
    AbstractUserSpecificManager,
    AbstractUserSpecificQuerySet,
)
from testapp.models import MySingleSignalModel


class AbstractUserSpecificQuerySetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.cqs = AbstractUserSpecificQuerySet()
        cls.user = User.objects.create(username="my-username")

    def test_default(self):
        self.assertEqual(self.cqs.default(self.user), self.cqs)

    def test_visible_for_regular(self):
        with self.assertRaisesMessage(NotImplementedError, "Please implement this method"):
            self.cqs.visible_for(self.user)

    def test_editable_for_regular(self):
        with self.assertRaisesMessage(NotImplementedError, "Please implement this method"):
            self.cqs.editable_for(self.user)

    def test_deletable_for_regular(self):
        with self.assertRaisesMessage(NotImplementedError, "Please implement this method"):
            self.cqs.deletable_for(self.user)


class TestUserSpecificManager(AbstractUserSpecificManager):
    pass


TestUserSpecificManager = TestUserSpecificManager.from_queryset(AbstractUserSpecificQuerySet)


class AbstractUserSpecificManagerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.manager = TestUserSpecificManager()
        cls.user = User.objects.create(username="my-username")

    def test_visible_for_regular(self):
        with self.assertRaisesMessage(NotImplementedError, "Please implement this method"):
            self.manager.visible_for(self.user)

    def test_editable_for_regular(self):
        with self.assertRaisesMessage(NotImplementedError, "Please implement this method"):
            self.manager.editable_for(self.user)

    def test_deletable_for_regular(self):
        with self.assertRaisesMessage(NotImplementedError, "Please implement this method"):
            self.manager.deletable_for(self.user)


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
        self.assertEqual(
            MySingleSignalModel.objects.visible_for(self.user).count(),
            len(self.object_list),
        )

    def test_editable_for_regular(self):
        self.assertGreater(len(self.object_list), 0)
        self.assertEqual(
            MySingleSignalModel.objects.editable_for(self.user).count(),
            len(self.object_list),
        )

    def test_deletable_for_regular(self):
        self.assertGreater(len(self.object_list), 0)
        self.assertEqual(
            MySingleSignalModel.objects.deletable_for(self.user).count(),
            len(self.object_list),
        )
