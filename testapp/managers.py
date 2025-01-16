from django.db import models

from ambient_toolbox.managers import GetOrNoneManagerMixin


class ModelWithSelectorQuerySet(models.QuerySet):
    pass


class ModelWithGetOrNoneManager(GetOrNoneManagerMixin, models.Manager):
    pass
