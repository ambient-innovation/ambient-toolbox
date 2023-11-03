from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers

from testapp.api.urls import model_router

router = routers.DefaultRouter()
router.registry.extend(model_router.registry)

urlpatterns = [
    # django Admin
    path("admin/", admin.site.urls),
    # REST Viewsets
    path("api/v1/", include(router.urls)),
    # Custom login view
    path("other/login/", TemplateView.as_view(template_name="testapp/test_template.html"), name="other-login-view"),
]
