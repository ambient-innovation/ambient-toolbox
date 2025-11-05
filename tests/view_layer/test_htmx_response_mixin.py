import json
from typing import ClassVar

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import TestCase
from django.views import generic

from ambient_toolbox.tests.mixins import RequestProviderMixin
from ambient_toolbox.view_layer.htmx_mixins import HtmxResponseMixin


class HtmxResponseMixinTest(RequestProviderMixin, TestCase):
    """Test suite for HtmxResponseMixin with 100% branch coverage."""

    class ViewTestView(HtmxResponseMixin, generic.View):
        hx_redirect_url = "https://my-url.com"
        hx_trigger = "myEvent"

        def get(self, request, *args, **kwargs):
            return HttpResponse(status=200)

    class TestViewWithTriggerDict(HtmxResponseMixin, generic.View):
        hx_trigger: ClassVar = {"myEvent": None}

        def get(self, request, *args, **kwargs):
            return HttpResponse(status=200)

    class TestViewWithComplexTriggerDict(HtmxResponseMixin, generic.View):
        hx_trigger: ClassVar = {"event1": "value1", "event2": {"key": "value"}}

        def get(self, request, *args, **kwargs):
            return HttpResponse(status=200)

    class TestViewNoHeaders(HtmxResponseMixin, generic.View):
        # Both hx_redirect_url and hx_trigger are None by default
        def get(self, request, *args, **kwargs):
            return HttpResponse(status=200)

    class TestViewOnlyRedirect(HtmxResponseMixin, generic.View):
        hx_redirect_url = "https://redirect-only.com"
        # hx_trigger is None

        def get(self, request, *args, **kwargs):
            return HttpResponse(status=200)

    class TestViewOnlyTrigger(HtmxResponseMixin, generic.View):
        # hx_redirect_url is None
        hx_trigger = "triggerOnly"

        def get(self, request, *args, **kwargs):
            return HttpResponse(status=200)

    class TestViewDynamicRedirect(HtmxResponseMixin, generic.View):
        def get_hx_redirect_url(self):
            return "https://dynamic-redirect.com"

        def get(self, request, *args, **kwargs):
            return HttpResponse(status=200)

    class TestViewDynamicTrigger(HtmxResponseMixin, generic.View):
        def get_hx_trigger(self):
            return "dynamicTrigger"

        def get(self, request, *args, **kwargs):
            return HttpResponse(status=200)

    class TestViewDynamicTriggerDict(HtmxResponseMixin, generic.View):
        def get_hx_trigger(self):
            return {"dynamicEvent": "dynamicValue"}

        def get(self, request, *args, **kwargs):
            return HttpResponse(status=200)

    def test_dispatch_functional(self):
        """Test dispatch with both redirect_url and trigger (string) set."""
        view = self.ViewTestView()

        response = view.dispatch(request=self.get_request(user=AnonymousUser()))

        self.assertIn("HX-Redirect", response)
        self.assertEqual(response["HX-Redirect"], "https://my-url.com")

        self.assertIn("HX-Trigger", response)
        self.assertEqual(response["HX-Trigger"], "myEvent")

    def test_dispatch_trigger_with_dict(self):
        """Test dispatch with trigger as a dict (with None value)."""
        view = self.TestViewWithTriggerDict()

        response = view.dispatch(request=self.get_request(user=AnonymousUser()))

        self.assertIn("HX-Trigger", response)
        self.assertEqual(response["HX-Trigger"], '{"myEvent": null}')

    def test_dispatch_trigger_with_complex_dict(self):
        """Test dispatch with trigger as a dict with complex values."""
        view = self.TestViewWithComplexTriggerDict()

        response = view.dispatch(request=self.get_request(user=AnonymousUser()))

        self.assertIn("HX-Trigger", response)
        # JSON should properly serialize the dict
        trigger_data = json.loads(response["HX-Trigger"])
        self.assertEqual(trigger_data["event1"], "value1")
        self.assertEqual(trigger_data["event2"]["key"], "value")

    def test_dispatch_no_headers(self):
        """Test dispatch when both redirect_url and trigger are None."""
        view = self.TestViewNoHeaders()

        response = view.dispatch(request=self.get_request(user=AnonymousUser()))

        # Verify headers are not set
        self.assertNotIn("HX-Redirect", response)
        self.assertNotIn("HX-Trigger", response)
        self.assertEqual(response.status_code, 200)

    def test_dispatch_only_redirect(self):
        """Test dispatch with only redirect_url set (no trigger)."""
        view = self.TestViewOnlyRedirect()

        response = view.dispatch(request=self.get_request(user=AnonymousUser()))

        self.assertIn("HX-Redirect", response)
        self.assertEqual(response["HX-Redirect"], "https://redirect-only.com")
        self.assertNotIn("HX-Trigger", response)

    def test_dispatch_only_trigger(self):
        """Test dispatch with only trigger set (no redirect_url)."""
        view = self.TestViewOnlyTrigger()

        response = view.dispatch(request=self.get_request(user=AnonymousUser()))

        self.assertNotIn("HX-Redirect", response)
        self.assertIn("HX-Trigger", response)
        self.assertEqual(response["HX-Trigger"], "triggerOnly")

    def test_get_hx_redirect_url_regular(self):
        """Test get_hx_redirect_url returns class attribute value."""
        view = self.ViewTestView()

        self.assertEqual(view.get_hx_redirect_url(), "https://my-url.com")

    def test_get_hx_redirect_url_none(self):
        """Test get_hx_redirect_url returns None when not set."""
        view = self.TestViewNoHeaders()

        self.assertIsNone(view.get_hx_redirect_url())

    def test_get_hx_trigger_regular(self):
        """Test get_hx_trigger returns class attribute value (string)."""
        view = self.ViewTestView()

        self.assertEqual(view.get_hx_trigger(), "myEvent")

    def test_get_hx_trigger_dict(self):
        """Test get_hx_trigger returns class attribute value (dict)."""
        view = self.TestViewWithTriggerDict()

        self.assertEqual(view.get_hx_trigger(), {"myEvent": None})

    def test_get_hx_trigger_none(self):
        """Test get_hx_trigger returns None when not set."""
        view = self.TestViewNoHeaders()

        self.assertIsNone(view.get_hx_trigger())

    def test_dynamic_redirect_url(self):
        """Test dispatch with overridden get_hx_redirect_url method."""
        view = self.TestViewDynamicRedirect()

        response = view.dispatch(request=self.get_request(user=AnonymousUser()))

        self.assertIn("HX-Redirect", response)
        self.assertEqual(response["HX-Redirect"], "https://dynamic-redirect.com")

    def test_dynamic_trigger_string(self):
        """Test dispatch with overridden get_hx_trigger method returning string."""
        view = self.TestViewDynamicTrigger()

        response = view.dispatch(request=self.get_request(user=AnonymousUser()))

        self.assertIn("HX-Trigger", response)
        self.assertEqual(response["HX-Trigger"], "dynamicTrigger")

    def test_dynamic_trigger_dict(self):
        """Test dispatch with overridden get_hx_trigger method returning dict."""
        view = self.TestViewDynamicTriggerDict()

        response = view.dispatch(request=self.get_request(user=AnonymousUser()))

        self.assertIn("HX-Trigger", response)
        self.assertEqual(response["HX-Trigger"], '{"dynamicEvent": "dynamicValue"}')
