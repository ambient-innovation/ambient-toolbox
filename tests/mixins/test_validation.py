from unittest import mock

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from testapp.models import ModelWithCleanMixin, ModelWithValidateConstraintsMixin


class CleanOnSaveMixinTest(TestCase):
    def test_clean_regular(self):
        obj = ModelWithCleanMixin()
        self.assertIsNone(obj.save())

    def test_clean_is_called(self):
        obj = ModelWithCleanMixin()
        with mock.patch.object(obj, "clean") as mocked_method:
            obj.save()

        mocked_method.assert_called_once()


class ValidateConstraintsOnSaveMixinTest(TestCase):
    def test_valid_object_is_saved(self):
        obj = ModelWithValidateConstraintsMixin(value=1)

        self.assertIsNone(obj.save())
        self.assertEqual(ModelWithValidateConstraintsMixin.objects.get(pk=obj.pk).value, 1)

    def test_clean_and_constraint_validation_are_called(self):
        obj = ModelWithValidateConstraintsMixin(value=1)
        with (
            mock.patch.object(obj, "clean") as mocked_clean,
            mock.patch.object(obj, "validate_constraints") as mocked_validate_constraints,
        ):
            obj.save()

        mocked_clean.assert_called_once()
        mocked_validate_constraints.assert_called_once()

    def test_clean_is_called_before_constraint_validation(self):
        obj = ModelWithValidateConstraintsMixin(value=1)
        call_order = []
        with (
            mock.patch.object(obj, "clean", side_effect=lambda: call_order.append("clean")),
            mock.patch.object(
                obj, "validate_constraints", side_effect=lambda: call_order.append("validate_constraints")
            ),
        ):
            obj.save()

        self.assertEqual(call_order, ["clean", "validate_constraints"])

    def test_constraint_violation_raises_validation_error(self):
        obj = ModelWithValidateConstraintsMixin(value=11)

        with self.assertRaisesMessage(ValidationError, "Value must not exceed 10."):
            obj.save()

        self.assertFalse(ModelWithValidateConstraintsMixin.objects.exists())

    def test_clean_violation_raises_validation_error(self):
        obj = ModelWithValidateConstraintsMixin(value=7)

        with self.assertRaisesMessage(ValidationError, "Seven is not a valid value."):
            obj.save()

    def test_bulk_create_bypasses_constraint_validation(self):
        with self.assertRaises(IntegrityError):
            ModelWithValidateConstraintsMixin.objects.bulk_create([ModelWithValidateConstraintsMixin(value=11)])
