from pathlib import Path

from django.conf import settings


def get_autodiscover_enabled() -> Path | str:
    """
    Switch to enable or disable function autodiscovery.
    Since the registry will be called on every request, we want to save overhead for projects that don't use it.
    """
    return getattr(settings, "AMBIENT_TOOLBOX_AUTODISCOVER_ENABLED", False)


def get_autodiscover_app_base_path() -> Path | str:
    """
    Base path of the application autodiscover should look for registered handlers.
    """
    return getattr(settings, "AMBIENT_TOOLBOX_AUTODISCOVER_APP_BASE_PATH", getattr(settings, "BASE_PATH", None))


def get_autodiscover_cache_key() -> str:
    """
    Cache key to store registered handlers in.
    """
    return getattr(settings, "AMBIENT_TOOLBOX_AUTODISCOVER_CACHE_KEY", "toolbox_autodiscover")


def get_autodiscover_logger_name() -> str:
    """
    Django logger name
    """
    return getattr(settings, "AMBIENT_TOOLBOX_AUTODISCOVER_LOGGER_NAME", "toolbox_autodiscover")
