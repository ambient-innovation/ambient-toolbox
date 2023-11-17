from rest_framework.routers import DefaultRouter

from testapp.api.views import MySingleSignalModelViewSet

model_router = DefaultRouter()
model_router.register(r"my-single-signal-model", MySingleSignalModelViewSet, basename="my-single-signal-model")
