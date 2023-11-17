from rest_framework import serializers

from testapp.models import MySingleSignalModel


class MySingleSignalModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MySingleSignalModel
        fields = [
            "id",
            "value",
        ]
