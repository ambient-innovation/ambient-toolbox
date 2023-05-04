from ambient_package_update.metadata.author import PackageAuthor
from ambient_package_update.metadata.constants import DEV_DEPENDENCIES
from ambient_package_update.metadata.package import PackageMetadata
from ambient_package_update.metadata.readme import ReadmeContent
from ambient_package_update.metadata.ruff_ignored_inspection import RuffIgnoredInspection

METADATA = PackageMetadata(
    package_name='ambient_toolbox',
    authors=[
        PackageAuthor(
            name='Ambient Digital',
            email='hello@ambient.digital',
        ),
    ],
    development_status='5 - Production/Stable',
    readme_content=ReadmeContent(
        tagline='Lots of helper functions and useful widgets',
        content="""## Features

* Useful classes and mixins for Django admin
* Coverage script for GitLab
* Extensions for DRF and GraphQL
* Mailing backends for Django
* Management commands for validating a projects test structure
* Object ownership tracking with timestamping
* Pattern for improved workflow with Django ORM
* Helper and util functions for many different use-cases
* Sentry plugins
* django-scrubber wrapper class
* Mixins and test classes for django (class-based) views
"""
    ),
    dependencies=[
        'Django>=2.2.28',
        'bleach>=1.4,<6',
        'python-dateutil>=2.5.3',
    ],
    optional_dependencies={
        'dev': [
            *DEV_DEPENDENCIES,
            'gevent~=22.10',
        ],
        'drf': [
            'djangorestframework>=3.8.2',
        ],
        'graphql': [
            'graphene-django>=2.2.0',
            'django-graphql-jwt>=0.2.1',
        ],
        'view-layer': [
            'django-crispy-forms>=1.4.0',
        ],
    },
    ruff_ignore_list=[
        RuffIgnoredInspection(key='N999', comment="Project name contains underscore, not fixable"),
        RuffIgnoredInspection(key='A003', comment="Django attributes shadow python builtins"),
        RuffIgnoredInspection(key='DJ001', comment="Django model text-based fields shouldn't be nullable"),
        RuffIgnoredInspection(key='B905', comment="Can be enabled when Python <=3.9 support is dropped"),
        RuffIgnoredInspection(key='DTZ001', comment="TODO will affect \"tz_today()\" method"),
        RuffIgnoredInspection(key='DTZ005', comment="TODO will affect \"tz_today()\" method"),
    ],
)
