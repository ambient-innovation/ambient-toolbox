import sys
from pathlib import Path
from unittest import mock

from django.apps import AppConfig, apps
from django.test import override_settings

from ambient_toolbox.apps import AmbientToolboxConfig


def test_app_config():
    app_config = apps.get_app_config("ambient_toolbox")

    assert isinstance(app_config, AppConfig)
    assert app_config.default_auto_field == "django.db.models.AutoField"
    assert app_config.name == "ambient_toolbox"


@override_settings(STATIC_ROLE_PERMISSIONS_PATH="/path/to/permissions")
@override_settings(STATIC_ROLE_PERMISSIONS_ENABLE_SYSTEM_CHECK=True)
@mock.patch("ambient_toolbox.apps.register")
def test_app_ready_static_role_permissions_checks_registered(mocked_register):
    config = AmbientToolboxConfig(app_name="ambient_toolbox", app_module=sys.modules[__name__])
    config.path = str(Path(__file__).resolve().parent)
    config.ready()

    assert mocked_register.call_count == 1


@override_settings(STATIC_ROLE_PERMISSIONS_PATH=None)
@override_settings(STATIC_ROLE_PERMISSIONS_ENABLE_SYSTEM_CHECK=True)
@mock.patch("ambient_toolbox.apps.register")
def test_app_ready_static_role_permissions_checks_not_registered_missing_path(mocked_register):
    config = AmbientToolboxConfig(app_name="ambient_toolbox", app_module=sys.modules[__name__])
    config.path = str(Path(__file__).resolve().parent)
    config.ready()

    assert mocked_register.call_count == 0


@override_settings(STATIC_ROLE_PERMISSIONS_PATH="/path/to/permissions")
@override_settings(STATIC_ROLE_PERMISSIONS_ENABLE_SYSTEM_CHECK=False)
@mock.patch("ambient_toolbox.apps.register")
def test_app_ready_static_role_permissions_checks_not_registered_checks_disabled(mocked_register):
    config = AmbientToolboxConfig(app_name="ambient_toolbox", app_module=sys.modules[__name__])
    config.path = str(Path(__file__).resolve().parent)
    config.ready()

    assert mocked_register.call_count == 0
