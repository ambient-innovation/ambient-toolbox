from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Tags, register
from django.utils.translation import gettext_lazy as _


class AmbientToolboxConfig(AppConfig):
    name = "ambient_toolbox"
    verbose_name = _("Ambient Toolbox")

    def ready(self):
        if getattr(settings, "STATIC_ROLE_PERMISSIONS_PATH", None) and not (
            getattr(settings, "STATIC_ROLE_PERMISSIONS_DISABLE_SYSTEM_CHECK", False)
        ):
            from ambient_toolbox.static_role_permissions.system_check import check_permissions_against_models

            register(check_permissions_against_models, Tags.models)
