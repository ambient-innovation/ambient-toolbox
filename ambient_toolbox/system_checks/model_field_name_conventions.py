from django.apps import apps
from django.conf import settings
from django.core import checks
from django.db.models import DateField, DateTimeField


def check_model_time_based_fields(*args, **kwargs):
    """
    Checks all model time fields ('DateField', 'DateTimeField') for a "correct" ending in their name.
    Inspired by: https://lukeplant.me.uk/blog/posts/enforcing-conventions-in-django-projects-with-introspection/
    """

    project_apps = [
        app.split(".")[-1] for app in settings.INSTALLED_APPS if app.startswith(settings.ROOT_URLCONF.split(".")[0])
    ]
    issue_list = []

    # Allowlists
    allowed_datetime_field_endings = getattr(settings, "ALLOWED_MODEL_DATETIME_FIELD_ENDINGS", ["_at"])
    allowed_date_field_endings = getattr(settings, "ALLOWED_MODEL_DATE_FIELD_ENDINGS", ["_date"])

    str_allowed_datetime_endings = ", ".join(allowed_datetime_field_endings)
    str_allowed_date_endings = ", ".join(allowed_date_field_endings)

    # Iterate all registered models...
    for model in apps.get_models():
        # Check if the model is from your project...
        if model._meta.app_label in project_apps:
            # Iterate over all fields...
            for field in model._meta.get_fields():
                # Case: DateTimeField, noqa: ERA001
                if isinstance(field, DateTimeField):
                    # Check field name ending against allowlist
                    if not field.name.lower().endswith(tuple(allowed_datetime_field_endings)):
                        issue_list.append(
                            checks.Warning(
                                f"DateTimeField '{model.__name__}.{field.name}' doesn't end with: "
                                f"{str_allowed_datetime_endings}.",
                                obj=field,
                                id="ambient_toolbox.W001",
                            )
                        )
                # Case: Date field, noqa: ERA001
                elif isinstance(field, DateField):
                    # Check field name ending against allowlist
                    if not field.name.lower().endswith(tuple(allowed_date_field_endings)):
                        issue_list.append(
                            checks.Warning(
                                f"DateField '{model.__name__}.{field.name}' doesn't end with: "
                                f"{str_allowed_date_endings}.",
                                obj=field,
                                id="ambient_toolbox.W002",
                            )
                        )

    return issue_list
