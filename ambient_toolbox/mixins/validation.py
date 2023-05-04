class CleanOnSaveMixin:
    """
    Mixin which ensures model-level validation ("clean()") is called on saving the current instance.
    """

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
