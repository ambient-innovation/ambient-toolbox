from django.conf import settings


def server_settings(request):
    return {"DEBUG_MODE": settings.DEBUG, "SERVER_URL": settings.SERVER_URL}
