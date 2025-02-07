from django.test import RequestFactory, override_settings

import settings
from ambient_toolbox.context_processors import server_settings


@override_settings(SERVER_URL="https://ambient.digital")
def test_server_settings_regular():
    request_factory = RequestFactory()
    assert server_settings(request=request_factory.get("/some-path/")) == {
        "DEBUG_MODE": settings.DEBUG,
        "SERVER_URL": "https://ambient.digital",
    }
