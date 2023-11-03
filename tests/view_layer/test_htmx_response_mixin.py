from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.views import generic

from ambient_toolbox.tests.mixins import RequestProviderMixin
from ambient_toolbox.view_layer.htmx_mixins import HtmxResponseMixin


class HtmxResponseMixinTest(RequestProviderMixin, TestCase):
    class TestView(HtmxResponseMixin, generic.View):
        hx_redirect_url = "https://my-url.com"
        hx_trigger = "myEvent"

    class TestViewWithTriggerDict(HtmxResponseMixin, generic.View):
        hx_trigger = {"myEvent": None}

    def test_dispatch_functional(self):
        view = self.TestView()

        response = view.dispatch(request=self.get_request(user=AnonymousUser()))

        self.assertIn("HX-Redirect", response)
        self.assertEqual(response["HX-Redirect"], "https://my-url.com")

        self.assertIn("HX-Trigger", response)
        self.assertEqual(response["HX-Trigger"], "myEvent")

    def test_dispatch_trigger_with_dict(self):
        view = self.TestViewWithTriggerDict()

        response = view.dispatch(request=self.get_request(user=AnonymousUser()))

        self.assertIn("HX-Trigger", response)
        self.assertEqual(response["HX-Trigger"], '{"myEvent": null}')

    def test_get_hx_redirect_url_regular(self):
        view = self.TestView()

        self.assertEqual(view.get_hx_redirect_url(), "https://my-url.com")

    def test_get_hx_trigger_regular(self):
        view = self.TestView()

        self.assertEqual(view.get_hx_trigger(), "myEvent")
