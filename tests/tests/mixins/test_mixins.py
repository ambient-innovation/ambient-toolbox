from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views import generic

from ambient_toolbox.tests.mixins import ClassBasedViewTestMixin


class TestView(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(status=202)

    def post(self, request, *args, **kwargs):
        return HttpResponse(status=203)

    def delete(self, request, *args, **kwargs):
        return HttpResponse(status=204)


class ClassBasedViewTestMixinTest(ClassBasedViewTestMixin, TestCase):
    view_class = TestView

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        factory = RequestFactory()
        cls.request = factory.get("/admin")
        cls.user = User.objects.create(username="my-username")

    def test_authentication_user_given(self):
        self._authentication(self.request, self.user), self.user
        self.assertEqual(self.request.user, self.user)

    def test_authentication_no_user_given(self):
        self._authentication(self.request, None), self.user
        self.assertEqual(self.request.user, AnonymousUser())

    def test_get_response_regular(self):
        response = self._get_response(method="get", user=self.user, data={"my_data": 42})
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 202)

    def test_get_regular(self):
        response = self.get()
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 202)

    def test_post_regular(self):
        response = self.post()
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 203)

    def test_delete_regular(self):
        response = self.delete()
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 204)
