from django.apps import AppConfig
from django.core.checks import Tags, register
from django.utils.translation import gettext_lazy as _

from ambient_toolbox.static_role_permissions.settings import (
    get_static_role_permissions_enable_system_check,
    get_static_role_permissions_path,
)


class AmbientToolboxConfig(AppConfig):
    name = "ambient_toolbox"
    verbose_name = _("Ambient Toolbox")

    def ready(self):
        # System checks for static role permission feature
        if get_static_role_permissions_path() and get_static_role_permissions_enable_system_check():
            from ambient_toolbox.static_role_permissions.system_check import check_permissions_against_models

            register(check_permissions_against_models, Tags.models)
