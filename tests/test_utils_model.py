from django.contrib.auth.models import Permission
from django.test import TestCase

from ambient_toolbox.utils import get_cached_related_obj, object_to_dict
from testapp.models import ForeignKeyRelatedModel, MySingleSignalModel


class UtilModelTest(TestCase):
    def test_object_to_dict_regular(self):
        obj = MySingleSignalModel.objects.create(value=17)
        self.assertEqual(object_to_dict(obj), {"value": obj.value})

    def test_object_to_dict_blocklist(self):
        obj = MySingleSignalModel.objects.create(value=17)
        self.assertEqual(object_to_dict(obj=obj, blocklisted_fields=["value"]), {})

    def test_object_to_dict_with_id_with_blocklist(self):
        obj = MySingleSignalModel.objects.create(value=17)
        self.assertEqual(object_to_dict(obj=obj, blocklisted_fields=["value"], include_id=True), {"id": obj.id})

    def test_with_id_no_blocklist(self):
        obj = MySingleSignalModel.objects.create(value=17)
        self.assertEqual(object_to_dict(obj, include_id=True), {"id": obj.id, "value": obj.value})

    def test_object_to_dict_valid_fields_append(self):
        obj = MySingleSignalModel.objects.create(value=17)
        dummy_instance = ForeignKeyRelatedModel(single_signal=obj)

        valid_data = object_to_dict(dummy_instance)

        self.assertIn("single_signal_id", valid_data)
        self.assertEqual(valid_data["single_signal_id"], obj.id)

    # --- Test get_cached_related_obj (happy path) ---
    def test_get_cached_related_obj_with_select_related(self):
        permission_obj = Permission.objects.select_related("content_type").first()
        with self.assertNumQueries(0):
            content_type = get_cached_related_obj(permission_obj, "content_type")
            self.assertIsNotNone(content_type)

    def test_get_cached_related_obj_with_prefetch_related(self):
        permission_obj = Permission.objects.prefetch_related("content_type").first()
        with self.assertNumQueries(0):
            content_type = get_cached_related_obj(permission_obj, "content_type")
            self.assertIsNotNone(content_type)

    def test_get_cached_related_obj_without_cached_and_silently_return_none(self):
        permission_obj = Permission.objects.first()
        with self.assertNumQueries(0):
            content_type = get_cached_related_obj(permission_obj, "content_type", silently_return_none=True)
            self.assertIsNone(content_type)

    # --- Test get_cached_related_obj (error path) ---

    def test_get_cached_related_obj_without_cached(self):
        permission_obj = Permission.objects.first()
        with self.assertNumQueries(0):
            with self.assertRaises(AttributeError) as ctx:
                get_cached_related_obj(permission_obj, "content_type")
            self.assertEqual(
                f'Field "content_type" not found in `fields_cache` of {permission_obj.__class__.__name__} object. '
                "Did you forget to use `select_related()` or `prefetch_related()`?",
                str(ctx.exception),
            )

    def test_get_cached_related_obj_with_non_existing_field(self):
        permission_obj = Permission.objects.first()
        with self.assertNumQueries(0):
            with self.assertRaises(AttributeError) as ctx:
                get_cached_related_obj(permission_obj, "foo")
            self.assertEqual(
                f'Field "foo" not found in `fields_cache` of {permission_obj.__class__.__name__} object. '
                "Did you forget to use `select_related()` or `prefetch_related()`?",
                str(ctx.exception),
            )

    def test_get_cached_related_obj_with_no_fk_field(self):
        permission_obj = Permission.objects.first()
        with self.assertNumQueries(0):
            with self.assertRaises(AttributeError) as ctx:
                get_cached_related_obj(permission_obj, "name")
            self.assertEqual(
                f'Field "name" not found in `fields_cache` of {permission_obj.__class__.__name__} object. '
                "Did you forget to use `select_related()` or `prefetch_related()`?",
                str(ctx.exception),
            )
