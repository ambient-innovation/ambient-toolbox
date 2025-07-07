from pathlib import Path

from django.conf import settings


def get_import_linter_root_packages() -> list[str]:
    return getattr(settings, "TOOLBOX_IMPORT_LINTER_ROOT_PACKAGES", settings.INSTALLED_APPS)


def get_import_linter_business_logic_apps() -> list[str]:
    return getattr(settings, "TOOLBOX_IMPORT_LINTER_BUSINESS_LOGIC_APPS", [])


def get_import_linter_blocklisted_apps() -> list[str]:
    return getattr(settings, "TOOLBOX_IMPORT_LINTER_BLOCKLISTED_APPS", [])


def get_import_linter_local_apps() -> list[str]:
    return getattr(settings, "TOOLBOX_IMPORT_LINTER_LOCAL_APPS", settings.INSTALLED_APPS)


def get_import_linter_path_to_toml() -> Path:
    return getattr(settings, "TOOLBOX_IMPORT_LINTER_PATH_TO_TOML", Path("./pyproject.toml"))
