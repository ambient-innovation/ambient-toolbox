from django.conf import settings
from django.http import HttpRequest


def server_settings(request: HttpRequest) -> dict:
    return {"DEBUG_MODE": settings.DEBUG, "SERVER_URL": settings.SERVER_URL}
