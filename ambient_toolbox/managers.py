from django.db import models


class AbstractPermissionMixin:
    """
    Mixin that provides an interface for a basic per-object permission system.
    Single objects cannot be checked individually, but can be matched with the corresponding query set.
    Please append further methods here, if necessary, to make them accessible at all inheriting classes
    (query sets AND managers).
    """

    def visible_for(self, user):
        raise NotImplementedError("Please implement this method")

    def editable_for(self, user):
        raise NotImplementedError("Please implement this method")

    def deletable_for(self, user):
        raise NotImplementedError("Please implement this method")


class AbstractUserSpecificQuerySet(models.QuerySet, AbstractPermissionMixin):
    """
    Extend this queryset in your model if you want to implement a visible_for functionality.
    """

    def default(self, user):
        return self

    def visible_for(self, user):
        raise NotImplementedError("Please implement this method")

    def editable_for(self, user):
        raise NotImplementedError("Please implement this method")

    def deletable_for(self, user):
        raise NotImplementedError("Please implement this method")


class AbstractUserSpecificManager(models.Manager, AbstractPermissionMixin):
    """
    The UserSpecificQuerySet has a method 'as_manger', which can be used for creating a default manager,
    which inherits all methods of the queryset and invokes the respective method of it's queryset, respectively.
    If the manager has to be declared separately for some reason, all queryset methods, have to be declared twice,
    once in the QuerySet, once in the manager class.
    For consistency reasons, both inherit from the same mixin, to ensure the equality of the method's names.
    """

    def visible_for(self, user):
        return self.get_queryset().visible_for(user)

    def editable_for(self, user):
        return self.get_queryset().editable_for(user)

    def deletable_for(self, user):
        return self.get_queryset().deletable_for(user)


class GloballyVisibleQuerySet(AbstractUserSpecificQuerySet):
    """
    Manager (QuerySet) for classes which do NOT have any visibility restrictions.
    """

    def visible_for(self, user):
        return self.all()

    def editable_for(self, user):
        return self.visible_for(user)

    def deletable_for(self, user):
        return self.visible_for(user)


class GetOrNoneManagerMixin:
    """
    This mixin provides a helper, similar to Django's "get_or_create" to fetch an object via "kwargs".
    It returns None if the object does not exist.
    This is more efficient than executing a query with "qs.first()" and check for "None" since "first()" will add
    ordering which we don't need.
    Attention: This will throw an "MultipleObjectsReturned" exception if more than one object matches the query params.
    """

    def get_or_none(self, **kwargs) -> models.Model | None:
        """
        Helper to fetch an object by its primary key.
        Returns None if the object does not exist.
        """
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None
