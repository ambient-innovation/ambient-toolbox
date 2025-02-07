from django.apps import AppConfig
from django.core.checks import Tags, register
from django.utils.translation import gettext_lazy as _

from ambient_toolbox.autodiscover.settings import get_autodiscover_enabled
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

        # Function autodiscovery feature
        if get_autodiscover_enabled():
            # Register all decorated functions before they get imported by something else which will break the
            # registration process since decorators are only executed the first time.
            from ambient_toolbox.autodiscover import decorator_based_registry

            decorator_based_registry.autodiscover()
