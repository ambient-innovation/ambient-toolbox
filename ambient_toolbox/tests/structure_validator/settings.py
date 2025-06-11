from django.conf import settings

# Test validator
TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST = []
_TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST = []


@property
def TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST():  # noqa: N802
    """
    The term "Whitelist" will be deprecated in 12.2 and move to "Allowlist".
    Until then, keep this for backwards compatibility but warn users about future deprecation.
    """

    import warnings

    warnings.warn(
        "The 'TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST' setting is deprecated and will be removed in a future version."
        "Use 'TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST' instead.",
        category=DeprecationWarning,
        stacklevel=1,
    )
    return _TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST


@TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST.setter
def TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST(value):  # noqa: N802
    """
    The term "Whitelist" will be deprecated in 12.2 and move to "Allowlist".
    Until then, keep this for backwards compatibility but warn users about future deprecation.
    """

    import warnings

    from django.conf import settings

    warnings.warn(
        "The 'TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST' setting is deprecated and will be removed in a future version."
        "Use 'TEST_STRUCTURE_VALIDATOR_FILE_ALLOWLIST' instead.",
        category=DeprecationWarning,
        stacklevel=1,
    )
    settings._TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST = value


try:
    TEST_STRUCTURE_VALIDATOR_BASE_DIR = settings.BASE_DIR
except AttributeError:
    TEST_STRUCTURE_VALIDATOR_BASE_DIR = ""

TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME = "apps"
TEST_STRUCTURE_VALIDATOR_APP_LIST = settings.INSTALLED_APPS
TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST = []
