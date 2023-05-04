from threading import local

try:
    # Mixin for compatible middleware (to be refactored when all projects use Django 2):
    # https://docs.djangoproject.com/en/2.1/topics/http/middleware/#writing-your-own-middleware
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

_user = local()


class CurrentUserMiddleware(MiddlewareMixin):
    """
    Middleware which stores request's user into global thread-safe variable.
    Must be introduced AFTER `django.contrib.auth.middleware.AuthenticationMiddleware`.
    """

    def process_request(self, request):
        _user.value = request.user

    def process_response(self, request, response):
        # this cleanup is required e.g. when running tests single-threaded
        try:
            del _user.value
        except AttributeError:
            pass
        return response

    @staticmethod
    def get_current_user():
        if hasattr(_user, 'value') and _user.value:
            return _user.value
