from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from ambient_toolbox.middleware.current_request import CurrentRequestMiddleware


class CreatedAtInfo(models.Model):
    created_at = models.DateTimeField(_("Created at"), default=now, db_index=True)

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, **kwargs):
        # just a fallback for old data
        if not self.created_at:
            self.created_at = now()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
            **kwargs,
        )


class CommonInfo(CreatedAtInfo):
    # Automatically add the model's fields to the 'update_fields' list if specified on save()
    ALWAYS_UPDATE_FIELDS = True

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Created by"),
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_created",
        on_delete=models.SET_NULL,
    )
    lastmodified_at = models.DateTimeField(_("Last modified at"), default=now, db_index=True)
    lastmodified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Last modified by"),
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_lastmodified",
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, **kwargs):
        self.lastmodified_at = now()
        current_user = self.get_current_user()
        self.set_user_fields(current_user)

        # Handle case that somebody only wants to update some fields
        if update_fields is not None and self.ALWAYS_UPDATE_FIELDS:
            update_fields = {"lastmodified_at", "lastmodified_by", "created_at", "created_by"}.union(update_fields)

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
            **kwargs,
        )

    @staticmethod
    def get_current_user():
        """
        Get the currently logged-in user over middleware.
        Can be overwritten to use e.g. other middleware or additional functionality.
        :return: user instance
        """
        return CurrentRequestMiddleware.get_current_user()

    def set_user_fields(self, user):
        """
        Set user-related fields before saving the instance.
        If no user with primary key is given the fields are not set.
        :param user: user instance of current user
        """
        if user and user.pk:
            if not self.pk:
                self.created_by = user
            self.lastmodified_by = user
