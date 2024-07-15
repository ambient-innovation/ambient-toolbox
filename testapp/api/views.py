from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from testapp.api import serializers
from testapp.models import MySingleSignalModel


class MySingleSignalModelViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.MySingleSignalModelSerializer

    def get_queryset(self):
        return MySingleSignalModel.objects.visible_for(self.request.user)
