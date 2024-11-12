import warnings

from django.apps import apps
from django.conf import settings
from django.core import checks
from django.db.models import ForeignKey, ManyToManyField, OneToOneField


def check_model_related_names_for_related_name(*args, **kwargs):
    """
    Checks all model relation fields ('ForeignKey', 'ManyToManyField', "OneToOneField") for having a defined
    "related_name". Either directly via the field or otherwise via the model meta-option "default_related_name".
    """

    if getattr(settings, "LOCAL_APPS", None):
        project_apps = [app.split(".")[-1] for app in settings.LOCAL_APPS]
    # Otherwise, we try some magic...
    else:
        project_apps = [
            app.split(".")[-1] for app in settings.INSTALLED_APPS if app.startswith(settings.ROOT_URLCONF.split(".")[0])
        ]

    # If we still don't get any apps, inform the user
    if len(project_apps) == 0:
        warnings.warn(
            "No local apps detected. Therefore, no model fields will be checked for missing related names.",
            Warning,
            stacklevel=2,
        )

    issue_list = []

    # Iterate all registered models...
    for model in apps.get_models():
        # Check if the model is from your project...
        if model._meta.app_label in project_apps:
            # If the model has a related name, this will be inherited to all relation fields and we're OK
            if model._meta.default_related_name:
                continue

            # Iterate over all fields...
            for field in model._meta.get_fields():
                # Check relation field types...
                if isinstance(field, (ForeignKey, ManyToManyField, OneToOneField)):
                    # Check if the field has a related name set...
                    if not field._related_name:
                        issue_list.append(
                            checks.Warning(
                                f"'{model.__name__}.{field.name}' doesn't have a related name set and neither does the "
                                "model define a default related name.",
                                obj=field,
                                id="ambient_toolbox.W003",
                            )
                        )

    return issue_list
