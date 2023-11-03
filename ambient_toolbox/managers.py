from django.db.models import Manager, QuerySet


class AbstractPermissionMixin:
    """
    Mixin that provides an interface for a basic per-object permission system.
    Single objects cannot be checked individually, but can be matched with the corresponding query set.
    Please append further methods here, if necessary, in order to make them accessible at all inheriting classes
    (query sets AND managers).
    """

    def visible_for(self, user):
        raise NotImplementedError("Please implement this method")

    def editable_for(self, user):
        raise NotImplementedError("Please implement this method")

    def deletable_for(self, user):
        raise NotImplementedError("Please implement this method")


class AbstractUserSpecificQuerySet(QuerySet, AbstractPermissionMixin):
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


class AbstractUserSpecificManager(Manager, AbstractPermissionMixin):
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
