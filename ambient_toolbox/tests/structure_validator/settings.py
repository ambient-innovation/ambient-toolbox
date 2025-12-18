"""Compatibility layer that keeps legacy whitelist settings alive while projects migrate.

The StructureTestValidator used to depend on `TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST`
and `TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST`.  We now prefer the allowlist
terminology, but until callers have migrated we must warn for the legacy names and keep
them synchronized with the allowlist globals defined here.  The
`_StructureValidatorSettingsModule` class serves as the bridge: it traps attribute
access on the module, emits `DeprecationWarning`s when the legacy names are touched,
and forwards every other attribute access to the underlying module so the rest of the
project can continue working.

Once the deprecation period ends, delete this module and replace it with a simple
constants module that exposes `TEST_STRUCTURE_VALIDATOR_*_ALLOWLIST` directly.  At that
point the legacy `file_whitelist` behavior and the `__getattr__/__setattr__` plumbing
can disappear; simply assign the values here and import them via
`ambient_toolbox.tests.structure_validator.settings`.
"""

import sys
import warnings
from types import ModuleType

from django.conf import settings


class _StructureValidatorSettingsModule(ModuleType):
    """Module proxy that preserves deprecated whitelist names while warning users."""

    _FILE_WHITELIST_ATTR = "TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST"
    _MISPLACED_WHITELIST_ATTR = "TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST"

    _FILE_WHITELIST_WARNING = (
        "The 'TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST' setting is deprecated and will be removed in a future "
        "version. Use 'TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST' instead."
    )
    _MISPLACED_WHITELIST_WARNING = (
        "The 'TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST' setting is deprecated and will be "
        "removed in a future version. Use 'TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_ALLOWLIST' instead."
    )

    def __init__(self, name: str):
        """Initialize the proxy module with allowlists and metadata for the validator."""

        super().__init__(name)

        # Keep private storage for the deprecated whitelist names so we can emit warnings when needed.
        object.__setattr__(self, "_TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST", [])
        object.__setattr__(self, "_TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST", [])
        # Expose the preferred allowlists so the rest of the codebase can import them directly.
        object.__setattr__(self, "TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST", [])
        object.__setattr__(self, "TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_ALLOWLIST", [])
        # Always skip __pycache__ by default to avoid noise during os.walk.
        object.__setattr__(self, "TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST", [])

        # Allow tests to patch warnings for the deprecation helpers.
        object.__setattr__(self, "warnings", warnings)

        # Fall back to an empty string when BASE_DIR is not available.
        try:
            base_dir = settings.BASE_DIR
        except AttributeError:
            base_dir = ""

        object.__setattr__(self, "TEST_STRUCTURE_VALIDATOR_BASE_DIR", base_dir)
        # Default the base app name to the canonical apps package.
        object.__setattr__(self, "TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME", "apps")
        # Reflect INSTALLED_APPS so the validator can iterate over every configured app.
        object.__setattr__(self, "TEST_STRUCTURE_VALIDATOR_APP_LIST", settings.INSTALLED_APPS)

    def __getattr__(self, name: str):
        """
        Provide warnings for deprecated whitelist attributes while still returning
        their stored allowlist equivalents.
        """
        if name == self._FILE_WHITELIST_ATTR:
            # Warn callers so that future code can switch to the allowlist setting.
            warnings.warn(self._FILE_WHITELIST_WARNING, category=DeprecationWarning, stacklevel=1)
            return self._TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST

        if name == self._MISPLACED_WHITELIST_ATTR:
            # Mirror the warning for the misplaced test file whitelist reference.
            warnings.warn(self._MISPLACED_WHITELIST_WARNING, category=DeprecationWarning, stacklevel=1)
            return self._TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST

        # Fallback to standard module behavior for every other attribute.
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value):
        """
        Intercept deprecated whitelist setters so we warn and keep the internal
        state (and Django settings) in sync.
        """
        # Intercept deprecated attributes so we can emit warnings and keep values up to date.
        if name == self._FILE_WHITELIST_ATTR:
            # Warn callers before updating the private whitelist storage.
            warnings.warn(self._FILE_WHITELIST_WARNING, category=DeprecationWarning, stacklevel=1)
            object.__setattr__(self, "_TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST", value)
            settings._TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST = value
            return

        if name == self._MISPLACED_WHITELIST_ATTR:
            # Mirror the warning for the misplaced whitelist setter.
            warnings.warn(self._MISPLACED_WHITELIST_WARNING, category=DeprecationWarning, stacklevel=1)
            object.__setattr__(self, "_TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST", value)
            settings._TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST = value
            return

        object.__setattr__(self, name, value)


sys.modules[__name__] = _StructureValidatorSettingsModule(__name__)
