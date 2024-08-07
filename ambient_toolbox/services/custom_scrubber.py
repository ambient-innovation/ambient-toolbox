import logging
from typing import ClassVar, Final

from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.contrib.auth.hashers import make_password
from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.db import OperationalError, connections


class ScrubbingError(RuntimeError):
    pass


class AbstractScrubbingService:
    DEFAULT_USER_PASSWORD: Final[str] = "Admin0404!"

    # Over-writable values
    keep_session_data: bool = False
    keep_scrubber_data: bool = False
    keep_django_admin_log: bool = False
    pre_scrub_functions: ClassVar = []
    post_scrub_functions: ClassVar = []

    def __init__(self):
        self._logger = logging.getLogger("django_scrubber")

    def _get_hashed_default_password(self):
        return make_password(self.DEFAULT_USER_PASSWORD)

    def _validation(self):
        if not settings.DEBUG:
            self._logger.warning("Attention! Has to run in DEBUG mode!")
            return False

        if "django_scrubber" not in settings.INSTALLED_APPS:
            self._logger.warning("Attention! django-scrubber needs to be installed!")
            return False

        if "django_scrubber" not in list(settings.LOGGING["loggers"].keys()):
            self._logger.warning("Attention! Logging for django-scrubber is not activated!")

        return True

    def process(self):
        self._logger.info("Start scrubbing process...")

        self._logger.info("Validating setup...")
        if not self._validation():
            self._logger.warning("Aborting process!")
            raise ScrubbingError("Scrubber settings validation failed")

        # Custom pre-scrubbing
        for name in self.pre_scrub_functions:
            self._logger.info(f'Pre-Scrubbing: Calling "{name}()"...')
            method = getattr(self, name)
            method()

        self._logger.info('Scrubbing data with "scrub_data"...')
        call_command("scrub_data")

        # Custom post-scrubbing
        for name in self.post_scrub_functions:
            self._logger.info(f'Post-Scrubbing: Calling "{name}()"...')
            method = getattr(self, name)
            method()

        # Empty django admin log (may contain user-related data)
        if not self.keep_django_admin_log:
            LogEntry.objects.all().delete()

        # Clear django session table
        if not self.keep_session_data:
            self._logger.info('Clearing data from "django_session" ...')
            # Sessions might contain private information and furthermore cannot be used anyway because we anonymised
            # all the users. Therefore, it is being cleared by default
            Session.objects.all().delete()

        # Reset scrubber data to avoid huge db dumps
        if not self.keep_scrubber_data:
            self._logger.info('Clearing data from "django_scrubber_fakedata" ...')
            # We truncate and don't scrub because the table is huge, and clearing on object-level might take a while.
            # Furthermore, we can avoid having a direct dependency on django-scrubber this way.
            cursor = connections["default"].cursor()
            try:
                cursor.execute("TRUNCATE TABLE django_scrubber_fakedata;")
            except OperationalError:
                # SQLite doesn't have "TRUNCATE"
                cursor.execute("DELETE FROM django_scrubber_fakedata;")

        self._logger.info("Scrubbing finished!")

        return True
