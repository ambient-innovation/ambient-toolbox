from django.db.models import QuerySet

from ambient_toolbox.selectors.base import Selector


class AbstractUserSpecificSelectorMixin:
    """
    Abstract selector mixin to inherit from to implement a basic permission pattern.
    Refer to the documentation for further details.
    """

    def visible_for(self, user_id: int) -> QuerySet:
        raise NotImplementedError

    def editable_for(self, user_id: int) -> QuerySet:
        raise NotImplementedError

    def deletable_for(self, user_id: int) -> QuerySet:
        raise NotImplementedError


class GloballyVisibleSelector(AbstractUserSpecificSelectorMixin, Selector):
    """
    Selector for classes which do NOT have any visibility restrictions. Use with caution!
    """

    def visible_for(self, user_id: int) -> QuerySet:
        return self.all()

    def editable_for(self, user_id: int) -> QuerySet:
        return self.visible_for(user_id=user_id)

    def deletable_for(self, user_id: int) -> QuerySet:
        return self.visible_for(user_id=user_id)
