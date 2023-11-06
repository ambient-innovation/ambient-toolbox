from django.db.models.signals import post_save, pre_save


class PermissionModelMixin:
    """
    Abstract model class to put permissions in which don't belong to a "real" database model.
    Take care that you have to set "Meta.default_permissions" to an empty tuple/list if you want to avoid having the
    Django default permissions created.
    Inspiration / Source: https://stackoverflow.com/a/37988537/1331671
    """

    class Meta:
        # No database table creation or deletion operations will be performed for this model.
        managed = False


class SaveWithoutSignalsMixin:
    """
    Mixin to provide a save method that temporarily unhooks all signals and restores them after save/error
    """

    def save_without_signals(self, *args, **kwargs):
        # Temporarily store signal receivers to restore them later
        pre_save_receivers = pre_save.receivers
        post_save_receivers = post_save.receivers

        # Clear signal receivers to make sure, that no signal is triggered when .save() is called
        pre_save.receivers = []
        post_save.receivers = []

        # Save without any signals
        instance = self.save(*args, **kwargs)

        # Restore signal receivers
        pre_save.receivers = pre_save_receivers
        post_save.receivers = post_save_receivers

        return instance
