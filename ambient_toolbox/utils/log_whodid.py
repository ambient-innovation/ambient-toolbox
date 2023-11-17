from django.db import models


def log_whodid(obj: models.Model, user) -> None:
    """
    Stores the given user as creator or editor of the given object
    """
    if hasattr(obj, "created_by") and obj.created_by is None:
        obj.created_by = user

    if hasattr(obj, "lastmodified_by"):
        obj.lastmodified_by = user
