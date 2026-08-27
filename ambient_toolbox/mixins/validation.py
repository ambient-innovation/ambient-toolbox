class CleanOnSaveMixin:
    """
    Mixin which ensures model-level validation ("clean()") is called on saving the current instance.
    """

    def save(self, *args, **kwargs):
        self._validate_before_save()
        super().save(*args, **kwargs)

    def _validate_before_save(self):
        self.clean()


class ValidateConstraintsOnSaveMixin(CleanOnSaveMixin):
    """
    Mixin which ensures model-level validation ("clean()") and constraint validation
    ("validate_constraints()") are called on saving the current instance.

    Constraints are checked the way a ModelForm checks them, so a violation surfaces as a
    ``ValidationError`` carrying the constraint's ``violation_error_message`` instead of an
    ``IntegrityError``. The constraint in the database stays the authority for concurrent writes -
    this only turns the common case into a catchable error.

    Costs one query per constraint per save. ``bulk_create()`` and ``QuerySet.update()`` bypass
    ``save()`` entirely; there the database constraint still holds, but raises an ``IntegrityError``.
    """

    def _validate_before_save(self):
        super()._validate_before_save()
        self.validate_constraints()
