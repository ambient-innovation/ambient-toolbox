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
from ambient_package_update.metadata.ruff_ignored_inspection import (
    RuffFilePatternIgnoredInspection,
    RuffIgnoredInspection,
)

claim = "Python toolbox of Ambient Digital containing an abundance of useful tools and gadgets."

METADATA = PackageMetadata(
    package_name="ambient-toolbox",
    github_package_group="ambient-innovation",
    licenser="Ambient Innovation: GmbH",
    authors=[
        PackageAuthor(
            name="Ambient Digital",
            email="hello@ambient.digital",
        ),
    ],
    maintainer=PackageMaintainer(name="Ambient Digital", url="https://ambient.digital/", email="hello@ambient.digital"),
    development_status="5 - Production/Stable",
    license=LICENSE_MIT,
    license_year=2012,
    claim=claim,
    readme_content=ReadmeContent(
        tagline=claim,
    ),
    dependencies=[
        f"Django>={SUPPORTED_DJANGO_VERSIONS[0]}",
        "python-dateutil>=2.5.3",
    ],
    supported_django_versions=SUPPORTED_DJANGO_VERSIONS,
    supported_python_versions=SUPPORTED_PYTHON_VERSIONS,
    has_migrations=True,
    optional_dependencies={
        "dev": [
            *DEV_DEPENDENCIES,
            "gevent~=25.1",
            "httpx~=0.28",
            "freezegun~=1.5",
        ],
        "drf": [
            "djangorestframework>=3.8.2",
        ],
        "graphql": [
            "graphene-django>=2.2.0",
            "django-graphql-jwt>=0.2.1",
        ],
        "import-linter": [
            "tomlkit~=0.13",
        ],
        "bleacher": [
            "nh3>=0.2,<1",
        ],
        "gitlab-coverage": [
            "httpx~=0.28",
        ],
        "sentry": [
            "sentry-sdk>=1.19.1",
        ],
        "view-layer": [
            "django-crispy-forms>=1.4.0",
        ],
    },
    ruff_ignore_list=[
        RuffIgnoredInspection(key="A005", comment="ruff flags valid Python modules"),
        RuffIgnoredInspection(key="N999", comment="Project name contains underscore, not fixable"),
        RuffIgnoredInspection(key="A003", comment="Django attributes shadow python builtins"),
        RuffIgnoredInspection(key="DJ001", comment="Django model text-based fields shouldn't be nullable"),
        RuffIgnoredInspection(key="B905", comment="Can be enabled when Python <=3.9 support is dropped"),
        RuffIgnoredInspection(key="DTZ001", comment='TODO will affect "tz_today()" method'),
        RuffIgnoredInspection(key="DTZ005", comment='TODO will affect "tz_today()" method'),
        RuffIgnoredInspection(
            key="RUF012", comment="Mutable class attributes should be annotated with `typing.ClassVar`"
        ),
        RuffIgnoredInspection(key="TD002", comment="Missing author in TO-DOs"),
        RuffIgnoredInspection(key="TD003", comment="Missing issue link on the line following this TO-DOs"),
        RuffIgnoredInspection(key="TRY002", comment="Checks for code that raises Exception directly."),
        RuffIgnoredInspection(
            key="TRY003",
            comment="Checks for long exception messages that are not defined in the exception class itself.",
        ),
    ],
    ruff_file_based_ignore_list=[
        RuffFilePatternIgnoredInspection(
            pattern="**/tests/missing_init/*.py",
            rules=[
                RuffIgnoredInspection(key="INP001", comment="Missing by design for a test case"),
            ],
        ),
    ],
)
