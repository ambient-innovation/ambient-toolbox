from django.contrib.auth.models import AbstractUser, User
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from ambient_toolbox.drf.tests import BaseViewSetTestMixin
from testapp.api import views
from testapp.models import MySingleSignalModel


class BaseApiTest(BaseViewSetTestMixin, TestCase):
    def get_default_api_user(self) -> AbstractUser:
        return User.objects.create(username="my-username", is_active=True)


class MySingleSignalModelApiViewTest(BaseApiTest):
    view_class = views.MySingleSignalModelViewSet

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Create list of objects
        cls.object_list = [
            MySingleSignalModel.objects.create(value=1),
            MySingleSignalModel.objects.create(value=2),
        ]

    def test_action_not_activated(self):
        with self.assertRaises(AttributeError):
            self.execute_request(
                method="post",
                url=reverse("my-single-signal-model-list"),
                viewset_kwargs={"post": "create"},
                user=self.default_api_user,
            )

    def test_list_authentication_required(self):
        self.validate_authentication_required(url=reverse("my-single-signal-model-list"), method="get", view="list")

    def test_list_regular(self):
        response = self.execute_request(
            method="get",
            url=reverse("my-single-signal-model-list"),
            viewset_kwargs={"get": "list"},
            user=self.default_api_user,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.object_list))
