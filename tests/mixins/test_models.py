from django.test import TestCase

from testapp.models import ModelWithSaveWithoutSignalsMixin


class SaveWithoutSignalsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.instance = ModelWithSaveWithoutSignalsMixin.objects.create()

    def test_signals_are_executed_on_normal_save_call(self):
        value_before = self.instance.value

        self.instance.save()
        self.instance.refresh_from_db()

        self.assertEqual(value_before + 1, self.instance.value)

    def test_signals_are_not_executed_on_save_without_signals_call(self):
        value_before = self.instance.value

        self.instance.save_without_signals()
        self.instance.refresh_from_db()

        self.assertEqual(value_before, self.instance.value)

    def test_signals_are_not_executed_on_save_without_signals_call_but_then_reexecuted_on_normal_save_call(self):
        value_before = self.instance.value

        self.instance.save_without_signals()
        self.instance.refresh_from_db()

        self.assertEqual(value_before, self.instance.value)

        self.instance.save()

        self.assertEqual(value_before + 1, self.instance.value)
