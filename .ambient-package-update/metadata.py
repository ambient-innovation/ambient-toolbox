from ambient_package_update.metadata.author import PackageAuthor
from ambient_package_update.metadata.constants import (
    DEV_DEPENDENCIES,
    LICENSE_MIT,
    SUPPORTED_DJANGO_VERSIONS,
    SUPPORTED_PYTHON_VERSIONS,
)
from ambient_package_update.metadata.maintainer import PackageMaintainer
from ambient_package_update.metadata.package import PackageMetadata
from ambient_package_update.metadata.readme import ReadmeContent
from ambient_package_update.metadata.ruff_ignored_inspection import RuffIgnoredInspection

METADATA = PackageMetadata(
    package_name="ambient_toolbox",
    module_name="ambient_toolbox",
    company="Ambient Innovation: GmbH",
    authors=[
        PackageAuthor(
            name="Ambient Digital",
            email="hello@ambient.digital",
        ),
    ],
    maintainer=PackageMaintainer(name="Ambient Digital", url="https://ambient.digital/", email="hello@ambient.digital"),
    min_coverage=86.30,
    development_status="5 - Production/Stable",
    license=LICENSE_MIT,
    license_year=2012,
    readme_content=ReadmeContent(
        tagline="Python toolbox of Ambient Digital containing an abundance of useful tools and gadgets.",
    ),
    dependencies=[
        "Django>=4.2",
        "python-dateutil>=2.5.3",
        # We keep this until we drop Python 3.8
        "pytz",
    ],
    supported_django_versions=SUPPORTED_DJANGO_VERSIONS,
    supported_python_versions=SUPPORTED_PYTHON_VERSIONS,
    has_migrations=True,
    optional_dependencies={
        "dev": [
            *DEV_DEPENDENCIES,
            "gevent~=23.9",
            "httpx~=0.27",
        ],
        "drf": [
            "djangorestframework>=3.8.2",
        ],
        "graphql": [
            "graphene-django>=2.2.0",
            "django-graphql-jwt>=0.2.1",
        ],
        "bleacher": [
            "nh3>=0.2,<1",
        ],
        "sentry": [
            "sentry-sdk>=1.19.1",
        ],
        "view-layer": [
            "django-crispy-forms>=1.4.0",
        ],
    },
    ruff_ignore_list=[
        RuffIgnoredInspection(key="N999", comment="Project name contains underscore, not fixable"),
        RuffIgnoredInspection(key="A003", comment="Django attributes shadow python builtins"),
        RuffIgnoredInspection(key="DJ001", comment="Django model text-based fields shouldn't be nullable"),
        RuffIgnoredInspection(key="B905", comment="Can be enabled when Python <=3.9 support is dropped"),
        RuffIgnoredInspection(key="DTZ001", comment='TODO will affect "tz_today()" method'),
        RuffIgnoredInspection(key="DTZ005", comment='TODO will affect "tz_today()" method'),
        RuffIgnoredInspection(key="TD002", comment="Missing author in TODO"),
        RuffIgnoredInspection(key="TD003", comment="Missing issue link on the line following this TODO"),
    ],
)
