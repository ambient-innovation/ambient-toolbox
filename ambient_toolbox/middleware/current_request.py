from threading import local

_threadlocal = local()


class CurrentRequestMiddleware:
    """
    Middleware which stores the current request in a threadlocal variable.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _threadlocal.request = request
        response = self.get_response(request)
        del _threadlocal.request
        return response

    @staticmethod
    def get_current_user():
        try:
            return _threadlocal.request.user
        except AttributeError:
            return None
