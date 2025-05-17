from pathlib import Path

BASE_PATH = Path(__file__).resolve(strict=True).parent

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ambient_toolbox",
    "testapp",
)

DEBUG = False

ALLOWED_HOSTS = ["localhost:8000"]

SECRET_KEY = "ASDFjklö123456890"

# Routing
ROOT_URLCONF = "testapp.urls"

STATIC_URL = "/static/"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": True,
        },
    },
]

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

# Mail backend
EMAIL_BACKEND_REDIRECT_ADDRESS = ""
EMAIL_BACKEND_DOMAIN_ALLOWLIST = ""

_EMAIL_BACKEND_DOMAIN_WHITELIST = ""
@property
def EMAIL_BACKEND_DOMAIN_WHITELIST():
    """
    The term "Whitelist" will be deprecated in 12.2 and move to "Allowlist".
    Until then, keep this for backwards compatibility but warn users about future deprecation.
    """

    import warnings
    warnings.warn(
        "The 'EMAIL_BACKEND_DOMAIN_WHITELIST' setting is deprecated and will be removed in a future version. Use 'EMAIL_BACKEND_DOMAIN_ALLOWLIST' instead.",
        category=DeprecationWarning,
        stacklevel=1,
    )
    return _EMAIL_BACKEND_DOMAIN_WHITELIST


@EMAIL_BACKEND_DOMAIN_WHITELIST.setter
def EMAIL_BACKEND_DOMAIN_WHITELIST(value):
    """
    The term "Whitelist" will be deprecated in 12.2 and move to "Allowlist".
    Until then, keep this for backwards compatibility but warn users about future deprecation.
    """

    import warnings
    from django.conf import settings

    warnings.warn(
        "The 'EMAIL_BACKEND_DOMAIN_WHITELIST' setting is deprecated and will be removed in a future version. Use 'EMAIL_BACKEND_DOMAIN_ALLOWLIST' instead.",
        category=DeprecationWarning,
        stacklevel=1,
    )
    settings._EMAIL_BACKEND_DOMAIN_WHITELIST = value

TIME_ZONE = "UTC"

LOCALE_PATHS = [BASE_PATH / "ambient_toolbox/locale"]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
