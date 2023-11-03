from rest_framework import serializers


class RecursiveField(serializers.Serializer):
    """
    Custom field for using the same serializer as a field. Useful for foreign keys to the same model.
    """

    def update(self, instance, validated_data):
        super().update(instance, validated_data)

    def create(self, validated_data):
        super().create(validated_data)

    def to_representation(self, value):
        # If the field is used with `many=True` we need to go one more parent level up to get the "real"
        # parent serializer.
        # Explanation: With `many=True` DRF creates an intermediate `ListSerializer`. It has `many=True`, so we'll end
        # up in the first if-case. If we do not use `many=True`, the "many" attribute is not set.
        if getattr(self.parent, "many", False):
            parent = self.parent.parent
        else:
            parent = self.parent
        serializer = parent.__class__(value, context=self.context)
        return serializer.data
