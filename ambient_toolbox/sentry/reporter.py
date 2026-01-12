import sys

import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger

# Important to not log the logger.error messages from django-q
# We only want to catch the exceptions, not the logger
ignore_logger("django-q")
ignore_logger("django_q")


class DjangoQ2SentryReporter:
    """
    Reporter implementation for Django Q2 that sends task failures to Sentry.

    This class is intended to be configured as the ``REPORTER`` in Django Q2
    so that it is instantiated and its :meth:`report` method is called
    whenever a task raises an unhandled exception.

    On first use, if the global Sentry SDK has not yet been initialized,
    the reporter will initialize it using the provided ``dsn`` and any
    additional keyword arguments. If Sentry has already been initialized
    elsewhere in the application, ``dsn`` may be omitted.

    When :meth:`report` is invoked, the reporter inspects the traceback to
    extract the Django Q2 task information from the stack, then sends the
    current exception to Sentry with a dedicated fingerprint and additional
    context (such as task id, name, and callable path) attached as extras.
    """

    def __init__(self, dsn=None, **kwargs):
        """
        Initialize a reporter that ensures Sentry is configured for Django Q tasks.

        If the Sentry SDK has not yet been initialized in this process, this
        constructor will call ``sentry_sdk.init`` with the provided ``dsn`` and
        any additional keyword arguments.

        If Sentry is already initialized (``sentry_sdk.is_initialized()`` returns
        ``True``), the constructor will not modify the existing configuration and
        the ``dsn`` and ``kwargs`` parameters are ignored.

        :param dsn: Sentry Data Source Name used to initialize the Sentry SDK
            when it has not yet been configured. This parameter is required if
            Sentry has not been initialized before.
        :param kwargs: Additional keyword arguments forwarded directly to
            ``sentry_sdk.init`` (for example, environment, release, integrations).
        :raises Exception: If Sentry is not yet initialized and no ``dsn`` is
            provided.
        """
        if not sentry_sdk.is_initialized():
            if not dsn:
                raise ValueError("If sentry hasn't been initialized before, dsn is required.")
            sentry_sdk.init(dsn, **kwargs)

    @staticmethod
    def return_task_from_stack(tb) -> dict:
        """
        Return task information from the stack trace if available.

        Used to tag and enrich Sentry events with django-q task details by
        extracting a `task` dict from the traceback frames (containing keys
        such as ``id`` and ``func``).

        :param tb: traceback object to inspect; if None, the current traceback is used.
        :return return_task: dict containing task information, or an empty dict if none found.
        """
        return_task = {}
        if not tb:
            tb = sys.exc_info()[2]

        # Walk to the deepest traceback (leaf)
        while getattr(tb, "tb_next", None) is not None:
            tb = tb.tb_next

        # Walk frames from leaf upwards until we find a valid task
        f = getattr(tb, "tb_frame", None)
        while f:
            locals_ = getattr(f, "f_locals", {})
            task = locals_.get("task")
            if isinstance(task, dict):
                # require both id and func
                if task.get("id", False) and task.get("func"):
                    return task
            f = getattr(f, "f_back", None)

        return return_task

    def report(self):
        """
        Report the currently handled exception to Sentry with Django-Q context.

        This method inspects the active exception from ``sys.exc_info()``, extracts
        the associated Django-Q task metadata from the traceback via
        :meth:`return_task_from_stack`, and sends the exception to Sentry.

        A new Sentry scope is created to:

        * Build a fingerprint based on the Django-Q integration, the task
          function path (if available), and the exception value, improving
          event grouping for task failures.
        * Attach task-related details (ID, name, function) as extras on the
          event so they are visible in Sentry without altering global scope.

        The exception is then captured using :func:`sentry_sdk.capture_exception`,
        passing the exception instance obtained from ``sys.exc_info()``.
        """
        # get exception triple
        _, exc_value, exc_tb = sys.exc_info()
        task = self.return_task_from_stack(exc_tb)

        with sentry_sdk.new_scope() as scope:
            func = task.get("func")
            if callable(func):
                func_path = f"{func.__module__}.{func.__qualname__}"
            elif isinstance(func, str):
                func_path = func
            else:
                func_path = "unknown"

            scope.fingerprint = [
                "django-q",
                func_path,
                str(exc_value),
            ]
            # store extras defensively as strings
            scope.set_extra("django_q_task_id", str(task.get("id", "")))
            scope.set_extra("django_q_task_name", str(task.get("name", "")))
            scope.set_extra("django_q_task_func", func_path)

            # capture the exception instance (more idiomatic for sentry)
            sentry_sdk.capture_exception(error=exc_value)
