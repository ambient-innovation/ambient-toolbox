from rest_framework.serializers import ModelSerializer


class BaseModelSerializer(ModelSerializer):
    def validate(self, data):
        """
        Call Model's clean() method to ensure model-level-validation
        :param data:
        :return:
        """
        cleaned_data = super().validate(data)
        instance = self.Meta.model(**cleaned_data)
        instance.clean()
        return cleaned_data


class CommonInfoSerializer(BaseModelSerializer):
    """
    This serializer should be used for all models that extend "CommonInfo". It adds the data for
    `lastmodified_by` and `created_by` when saving a model through the serializer.
    This cannot be done in the model's `save` function, since the request is required.
    """

    def validate(self, data):
        data = super().validate(data)
        request = self.context.get("request", None)

        if request.user:
            data["lastmodified_by"] = request.user
            if not self.instance:
                # If this is a new instance, set created_by
                data["created_by"] = request.user

        return data
