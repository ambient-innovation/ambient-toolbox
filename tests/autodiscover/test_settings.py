from django.conf import settings
from django.test import override_settings

from ambient_toolbox.autodiscover.settings import (
    get_autodiscover_app_base_path,
    get_autodiscover_cache_key,
    get_autodiscover_enabled,
    get_autodiscover_logger_name,
)


@override_settings(AMBIENT_TOOLBOX_AUTODISCOVER_ENABLED=True)
def test_get_autodiscover_enabled_is_set():
    assert get_autodiscover_enabled() is True


def test_get_autodiscover_enabled_default_used():
    assert get_autodiscover_enabled() is False


@override_settings(AMBIENT_TOOLBOX_AUTODISCOVER_APP_BASE_PATH="/path/to/autodiscover")
def test_get_autodiscover_app_base_path_is_set():
    assert get_autodiscover_app_base_path() == "/path/to/autodiscover"


def test_get_autodiscover_app_base_path_default_used():
    assert get_autodiscover_app_base_path() == settings.BASE_PATH


@override_settings(AMBIENT_TOOLBOX_AUTODISCOVER_CACHE_KEY="new_cache_key")
def test_get_autodiscover_cache_key_is_set():
    assert get_autodiscover_cache_key() == "new_cache_key"


def test_get_autodiscover_cache_key_default_used():
    assert get_autodiscover_cache_key() == "toolbox_autodiscover"


@override_settings(AMBIENT_TOOLBOX_AUTODISCOVER_LOGGER_NAME="my_logger")
def test_get_autodiscover_logger_name_is_set():
    assert get_autodiscover_logger_name() == "my_logger"


def test_get_autodiscover_logger_name_default_used():
    assert get_autodiscover_logger_name() == "toolbox_autodiscover"
