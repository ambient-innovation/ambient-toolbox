import sentry_sdk
from graphene_django.views import GraphQLView


class SentryGraphQLView(GraphQLView):
    """
    Graphene sentries are all merged into a single issue.
    This code wraps the normal GraphQLView with a handler that deals with Sentry errors properly.

    Copied from:
    https://github.com/phalt/graphene-django-sentry/blob/master/graphene_django_sentry/views.py

    This class was tested with the following versions of these libraries. You must have them installed. If your
    version does not meet the requirements this code may break. Use on your own risk.
        * sentry_sdk >= 0.13.0
        * graphene_django >=2.9.1, <3.0
    """

    def execute_graphql_request(self, *args, **kwargs):
        """Extract any exceptions and send them to Sentry"""
        result = super().execute_graphql_request(*args, **kwargs)

        if result.errors:
            self._capture_sentry_exceptions(result.errors)
        return result

    def _capture_sentry_exceptions(self, errors):
        """
        Capture each exception and get its original error to send it to sentry.
        """
        for error in errors:
            try:
                sentry_sdk.capture_exception(error.original_error)
            except AttributeError:
                sentry_sdk.capture_exception(error)
