from django.apps import AppConfig, apps
from django.contrib.auth import get_permission_codename
from django.core.checks import Warning  # noqa: A004

from ambient_toolbox.static_role_permissions.permissions import load_static_role_permissions


def collect_model_permissions(app_configs: list[AppConfig]) -> set[str]:
    """
    Go through all apps/models and collect default + custom permissions.
    """
    all_model_permissions = set()

    for app_config in app_configs:
        # iterate over all models in all apps
        for klass in app_config.get_models():
            opts = klass._meta
            app_label = app_config.label

            # collect default permissions
            for action in opts.default_permissions:
                codename = get_permission_codename(action, opts)
                all_model_permissions.add(f"{app_label}.{codename}")
            # collect custom permissions
            for codename, _ in opts.permissions:
                all_model_permissions.add(f"{app_label}.{codename}")

    return all_model_permissions


def check_permissions_against_models(app_configs: list[AppConfig] | None = None, **kwargs) -> list:
    """
    Check whether static role permissions exist in models.
    We do this to ensure full compatibility with Django's permission system.
    """
    if not app_configs:
        app_configs = apps.get_app_configs()

    errors = []
    model_permissions_set = collect_model_permissions(app_configs)
    role_permissions_dict = load_static_role_permissions()

    # check static permissions against model permissions
    for role_name, role_permissions_set in role_permissions_dict.items():
        for permission in role_permissions_set:
            if permission not in model_permissions_set:
                errors.append(
                    Warning(
                        "Permission does not exist in any model.",
                        obj=f"'{permission}' (Role '{role_name}')",
                    )
                )
                break

    return errors
