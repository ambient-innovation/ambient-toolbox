"""Compatibility layer that keeps legacy whitelist settings alive.

The StructureTestValidator used to rely on `TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST`
and `TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST`.  We now prefer the
allowlist terminology, but until the callers have migrated we need to warn when the
old names are accessed and keep them synchronized with the allowlist globals defined
here.  The `_StructureValidatorSettingsModule` exists solely to trap attribute access
and emit `DeprecationWarning`s while still behaving like a normal module.

Once Django projects have migrated away from the deprecated setting names we can
remove this module entirely and replace it with a plain constants module that
exposes the new `TEST_STRUCTURE_VALIDATOR_*_ALLOWLIST` lists directly.  At that
point the original whitelist warnings and the custom `__getattr__/__setattr__`
hoops can disappear; simply define the values here and import them directly from
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
        """Initialize the proxy with default allowlists and project metadata."""

        super().__init__(name)

        # Prepare both the old-style whitelist storage and the new allowlists.
        object.__setattr__(self, "_TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST", [])
        object.__setattr__(self, "_TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST", [])
        object.__setattr__(self, "TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST", [])
        object.__setattr__(self, "TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_ALLOWLIST", [])
        object.__setattr__(self, "TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST", [])

        # Expose warnings so callers can patch it for tests that assert DeprecationWarning usage.
        object.__setattr__(self, "warnings", warnings)

        # Fall back to an empty string when BASE_DIR is not configured.
        try:
            base_dir = settings.BASE_DIR
        except AttributeError:
            base_dir = ""

        object.__setattr__(self, "TEST_STRUCTURE_VALIDATOR_BASE_DIR", base_dir)
        object.__setattr__(self, "TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME", "apps")
        object.__setattr__(self, "TEST_STRUCTURE_VALIDATOR_APP_LIST", settings.INSTALLED_APPS)

    def __getattr__(self, name: str):
        """
        Provide warnings for deprecated whitelist attributes while still returning
        their stored allowlist equivalents.
        """
        if name == self._FILE_WHITELIST_ATTR:
            warnings.warn(self._FILE_WHITELIST_WARNING, category=DeprecationWarning, stacklevel=1)
            return self._TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST

        if name == self._MISPLACED_WHITELIST_ATTR:
            warnings.warn(self._MISPLACED_WHITELIST_WARNING, category=DeprecationWarning, stacklevel=1)
            return self._TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST

        return super().__getattribute__(name)

    def __setattr__(self, name: str, value):
        """
        Intercept deprecated whitelist setters so we warn and keep the internal
        state (and Django settings) in sync.
        """
        # Intercept deprecated attributes so we can emit warnings and keep values up to date.
        if name == self._FILE_WHITELIST_ATTR:
            warnings.warn(self._FILE_WHITELIST_WARNING, category=DeprecationWarning, stacklevel=1)
            object.__setattr__(self, "_TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST", value)
            settings._TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST = value
            return

        if name == self._MISPLACED_WHITELIST_ATTR:
            warnings.warn(self._MISPLACED_WHITELIST_WARNING, category=DeprecationWarning, stacklevel=1)
            object.__setattr__(self, "_TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST", value)
            settings._TEST_STRUCTURE_VALIDATOR_MISPLACED_TEST_FILE_WHITELIST = value
            return

        object.__setattr__(self, name, value)


sys.modules[__name__] = _StructureValidatorSettingsModule(__name__)
