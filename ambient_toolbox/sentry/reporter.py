import sys

import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger

# Important to not log the logger.error messages from django-q
# We only want to catch the exceptions, not the logger
ignore_logger("django-q")
ignore_logger("django_q")


class DjangoQ2SentryReporter:
    def __init__(self, dsn=None, **kwargs):
        if not sentry_sdk.is_initialized():
            if not dsn:
                raise Exception("If sentry hasn't been initialized before, dsn is required.")
            sentry_sdk.init(dsn, **kwargs)

    @staticmethod
    def return_task_from_stack(tb) -> dict:
        """
        Function returns task information from stack trace if available
        Used to tag
        :param tb: traceback
        :return return_task: dict
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
