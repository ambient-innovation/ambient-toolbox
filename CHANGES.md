# Changelog

**12.4.4** (2025-07-07)
  * Fixed a bug leading to import linter validation always returning "true"

**12.4.3** (2025-07-07)
  * Added shell output for better UX for import linter validation command

**12.4.2** (2025-07-07)
  * Fixed import-linter tests and increased project coverage border

**12.4.1** (2025-07-07)
  * Fixed issue with import-linter validation command

**12.4.0** (2025-07-07)
  * Added helpers for the "import-linter" package
  * Fixed missing setup info in system check docs

**12.3.0** (2025-06-18)
  * New function returning the starting date of the previous quarter for a given date

**12.2.3** (2025-06-17)
  * Fixed issue with null variable in GitLab coverage service

**12.2.2** (2025-06-16)
  * Added missing variable to GitLab coverage docs

**12.2.1** (2025-06-04)
  * Added dependency extra for GitLab coverage

**12.2.0** (2025-06-04)
  * Added management command to wrap GitLab coverage validation

**12.1.9** (2025-05-30)
  * Fixed linter issue via ambient-package-update

**12.1.8** (2025-05-30)
  * Fixed linter issue via ambient-package-update

**12.1.7** (2025-05-30)
  * Maintenance updates via ambient-package-update

**12.1.6** (2025-05-29)
  * Maintenance updates via ambient-package-update
  * Updated gevent due to compiling issues in the pipeline

**12.1.5** (2025-04-03)
  * Maintenance updates via ambient-package-update
  * Improved some conditions in permission fixtures feature

**12.1.4** (2025-03-21)
  * Fixed a show-stopper bug in the autodiscover feature

**12.1.3** (2025-03-20)
  * Fixed typos in the documentation

**12.1.2** (2025-03-19)
  * Fixed wrong import in scrubber docs

**12.1.1** (2025-02-07)
  * Added test for context processor

**12.1.0** (2025-02-07)
  * New feature: Function registry with autodiscovery

**12.0.2** (2025-02-07)
  * Refactored test suite and some code to remove pytest warnings

**12.0.1** (2025-02-06)
  * Dropped `pytz` dependency and refactored some code to work with Python >= 3.9 builtins
  * Fixed some typos in the docs
  * Extended metadata for ambient-package-update

**12.0.0** (2025-02-03)
  * **Breaking change:**  Renamed `STATIC_ROLE_PERMISSIONS_DISABLE_SYSTEM_CHECK` to
  `STATIC_ROLE_PERMISSIONS_ENABLE_SYSTEM_CHECK` since negations are harder to understand
  * Improved implementation of role permission settings
  * Minor internal changes due to new ruff rules

**11.7.1** (2025-01-17)
  * Fixed bug in `get_start_and_end_date_from_calendar_week` leading to the first calendar week being determined incorrectly

**11.7.0** (2025-01-16)
  * Added `GetOrNoneManagerMixin` manager mixin to provide `get_or_none()`

**11.6.0** (2024-11-20)
  * Added `detect_ghost_tables` management command

**11.5.5** (2024-11-20)
  * Moved permission check to "apps.ready()" method
  * Internal updates via `ambient-package-update`

**11.5.4** (2024-11-15)
  * Internal updates via `ambient-package-update`

**11.5.3** (2024-11-12)
  * Fixed bug leading to non-working system checks in date-time and related name checks

**11.5.2** (2024-10-15)
  * Improved date determination of `get_start_and_end_date_from_calendar_week`

**11.5.1** (2024-10-14)
* Added Python 3.13 support
* Added Djade linter to pre-commit
* Improved GitHub action triggers
* Updated dev dependencies and linters

**11.5.0** (2024-09-29)
* Added system check to ensure that all model relation fields have a related name, either directly set or via the model
  meta-option "default_related_name".

**11.4.0** (2024-09-24)
  * Added system check to enforce naming conventions for DateFields and DateTimeFields

**11.3.0** (2024-09-17)
  * Added date util functions `get_current_year` and `check_date_is_weekend`
  * Improved date utils docs

**11.2.4** (2024-09-11)
  * Added GitHub action trigger for PRs

**11.2.3** (2024-09-11)
  * Fixed coverage setup due to GitHub changes
  * Optimised sentry helper tests to make them version agnostic

**11.2.2** (2024-09-11)
  * Fixed issue with package name
  * Updated linters

**11.2.1** (2024-08-12)
  * Fixed test matrix

**11.2.0** (2024-08-12)
  * Added Django 5.1 support

**11.1.2** (2024-07-19)
  * Added limitation paragraph to object ownership admin documentation

**11.1.1** (2024-07-19)
  * Fixed a bug leading to missing docs

**11.1.0** (2024-07-18)
  * Added static role permission feature

**11.0.3** (2024-07-16)
  * Added SECURITY.md
  * Updated linters
  * Internal updates via `ambient-package-update`

**11.0.2** (2024-07-16)
  * Fixed GitHub actions bug

**11.0.1** (2024-07-16)
  * Updated GitHub actions

**11.0.0** (2024-07-15)
  * Dropped Python 3.8 support
  * Replaced underlying bleach package with nh3 in `BleacherMixin`
  * Added new Ruff linting rules

**10.1.1** (2024-07-08)
  * Fixed documentation nitpick

**10.1.0** (2024-07-08)
  * Added management command `validate_translation_file_integrity`

**10.0.4** (2024-06-20)
  * Linted docs with `blacken-docs` via `ambient-package-update`

**10.0.3** (2024-06-20)
  * Made translation helper management command work with string-based locale paths

**10.0.2** (2024-06-20)
  * Made the "default" translation command more visible
  * Internal updates via `ambient-package-update`

**10.0.1** (2024-06-14)
  * Internal updates via `ambient-package-update`

**10.0.0** (2024-04-11)
  * Dropped Django 3.2 & 4.1 support (via `ambient-package-update`)
  * Internal updates via `ambient-package-update`

**9.6.5** (2024-04-10)
  * Added SQLite support for `AbstractScrubbingService`

**9.6.4** (2024-03-28)
  * Added convenience feature for `create_translation_file` so the user can omit the `--lang` param if there is only
one language
  * Added `pytz` as a dependency until we can drop it when removing Python 3.8 compat

**9.6.3** (2024-03-04)
  * Fixed a bug in the documentation

**9.6.2** (2024-03-04)
  * Fixed a bug in the documentation

**9.6.1** (2024-03-04)
  * Improved error handling in `create_translation_file`

**9.6.0** (2024-02-29)
  * Added management command `create_translation_file` to smoothen the workflow with translation files
  * Added docs about pipeline checks for translation files

**9.5.1** (2024-02-28)
  * Fixed bug in coverage script that a set `GITLAB_CI_DISABLE_COVERAGE` would always skip coverage check
  * Bugfix in `number_to_string` for more recent Django versions

**9.5.0** (2024-02-02)
  * Added django message test helper method `assert_message_not_in_request`

**9.4.4** (2024-01-22)
  * Downgraded sphinx to 7.1.* for Python 3.8 compatability

**9.4.3** (2024-01-22)
  * Updated sphinx packages

**9.4.2** (2024-01-22)
  * Fixed an SQLite bug in "PermissionSetupService"

**9.4.1** (2024-01-12)
  * Updated testing docs

**9.4.0** (2023-12-05)
  * Support for Django 5.0 added

**9.3.2** (2023-12-01)
  * Handled NullPointer in GitLab coverage script

**9.3.1** (2023-11-27)
  * Fixed wrong path in validator documentation
  * Added missing German translation

**9.3.0** (2023-11-24)
  * Added auth password validator for special chars `SpecialCharValidator`

**9.2.1** (2023-11-21)
  * Fixed crash in GitLab coverage service due to `check=True`

**9.2.0** (2023-11-17)
  * Added migration docs to Readme
  * Added migration check to GitHub actions
  * Switched formatter from `black` to `ruff`
  * Enforcing minimum coverage in CI/CD pipeline
  * Further updates from ambient updater package
  * Updated GitHub action versions
  * Fixes typos

**9.1.5** (2023-10-31)
  * Coverage service fixed crash on zero pipelines
  * Added default `develop` for `GITLAB_CI_COVERAGE_TARGET_BRANCH` in GitLab coverage service

**9.1.4** (2023-10-29)
  * Added return value for `WhitelistEmailBackend`
  * Removed old author annotations

**9.1.3** (2023-10-11)
  * Fixed scrubber tests

**9.1.2** (2023-10-11)
  * Fixed bug in scrubber wrapper to raise an exception instead of returning only "False"

**9.1.1** (2023-10-04)
  * Fixed bug with unset CI variable in GitLab coverage checker

**9.1.0** (2023-10-04)
  * Added coverage diff to pipeline
  * Added Python 3.12 support
  * Updated internal linter packages

**9.0.7** (2023-09-08)
  * Meta updates via ambient-package-update

**9.0.6** (2023-09-08)
  * Meta updates via ambient-package-update

**9.0.5** (2023-08-14)
  * Fixed linting issues due to more strict ruff rules
  * Added some tests

**9.0.4** (2023-08-02)
  * Improved `CommonInfoAdminMixin` documentation and implementation

**9.0.3** (2023-08-02)
  * Reverted redundant generic test case (was already covered)

**9.0.2** (2023-08-02)
  * Added generic test case for new attribute from v9.0.1 to `BaseViewPermissionTestMixin`

**9.0.1** (2023-08-02)
  * Added customisation for custom login view name for `DjangoPermissionRequiredMixin`

**9.0.0** (2023-07-25)
  * Dropped support for deprecated Django versions 2.2, 3.1 & 4.0

**8.4.3** (2023-07-25)
  * Updated linting and metadata

**8.4.2** (2023-07-24)
  * Fixed a bug and a compatability issue with "django-safedelete" with `CommonInfo.save()`

**8.4.1** (2023-07-17)
  * Improved `Model.save()` compatibility for `CommonInfo.save()`

**8.4.0** (2023-05-22)
  * Added improved `CurrentRequestMiddleware` in favour of deprecated `CurrentUserMiddleware`
  * Some minor maintenance changes

**8.3.5** (2023-05-16)
  * Moved sentry import for sentry helper inside of function to avoid problems with compatability

**8.3.4** (2023-05-12)
  * Added docs about integration testing for permission fixtures

**8.3.3** (2023-05-12)
  * Fixed Python 3.8 compat

**8.3.2** (2023-05-11)
  * Updated docs about permission settings setup

**8.3.1** (2023-05-11)
  * Updated docs about permission feature limitations

**8.3.0** (2023-05-11)
  * Added improved Django group permission fixtures

**8.2.1** (2023-05-10)
  * Updated package linters
  * Added release scripts for windows and UNIX

**8.2.0** (2023-05-05)
  * Add sentry event scrubber
  * Add optional dependency sentry-sdk

**8.1.1** (2023-05-04)
  * Updated migration docs

**8.1.0** (2023-05-04)
  * Support for Django 4.2 added

**8.0.2** (2023-05-04)
  * Bugfix in documentation

**8.0.1** (2023-05-04)
  * Added migration guide to docs

**8.0.0** (2023-05-01)
  * Rename and re-release package as "ambient-toolbox"
  * Extracted class-based mails as [django-pony-express](https://test.pypi.org/project/django-pony-express/)

**7.0.0** (2023-03-28)
  * *Breaking change:* Dropped Python 3.7 support due to end of lifetime
  * Added `ALWAYS_UPDATE_FIELDS` flag to `CommonInfo` model
  * Added `ruff` linter and replaced `flake8` and `isort` with it
  * Excluded not officially supported Python versions for certain Django releases for test matrix

**6.12.0** (2023-03-16)
  * Added `validate_test_structure` management command for validating project test structure
  * Fixed syntax error in docs
  * Fixed typo in docstring of `concat` method
  * Improved code in test app

**6.11.0** (2023-02-19)
  * Added `HtmxResponseMixin` for Django views
  * Added missing `object` class attribute to `ToggleView`
  * Updated local lint, build and test suite to Python 3.11
  * Updated readme file for contribution

**6.10.1** (2023-02-13)
  * Updated bug in documentation

**6.10.0** (2023-02-13)
  * Added test mixin `DjangoMessagingFrameworkTestMixin`
  * Added python 3.11 to test matrix and supported versions

**6.9.2** (2023-02-06)
  * Updated `pre-commit` packages

**6.9.1** (2023-01-25)
  * Set version border for dependency "bleach" because of breaking changes

**6.9.0** (2023-01-18)
  * Added "GITLAB_CI_DISABLE_COVERAGE" flag to coverage script for GitLab pipeline
  * Fixed typo in the docs

**6.8.4** (2023-01-11)
  * Moved changelog to "CHANGES.md" to make Dependabot understand/find it

**6.8.3** (2023-01-11)
  * Fixed bug with filtering in EmailTestService for subject passing a gettext_lazy object (second occurrence)

**6.8.2** (2023-01-11)
  * Fixed bug with filtering in EmailTestService for subject passing a gettext_lazy object

**6.8.1** (2022-12-20)
  * Fixed broken init file

**6.8.0** (2022-12-19)
  * Added `SaveWithoutSignalsMixin` model mixin

**6.7.0** (2022-11-25)
  * Added `Selector` base class
  * Added `AbstractUserSpecificSelectorMixin` and `GloballyVisibleSelector` helpers for selector pattern
  * Added documentation for new selector pattern
  * Added `django-upgrade` to linting
  * Added date helper `get_first_and_last_of_month`
  * Updated linting tools `black` & `pyupgrade`
  * Added `pyupgrade` and `django-upgrade` to pipeline

**6.6.3** (2022-11-18)
  * Fixed `BaseViewPermissionTestMixin` to work with custom user models

**6.6.2** (2022-10-12)
  * Updated documentation of mixin `PermissionModelMixin` in regard to a caveat with default permissions

**6.6.1** (2022-10-12)
  * Bugfix in documentation of mixin `PermissionModelMixin`

**6.6.0** (2022-10-12)
  * Added model mixin `PermissionModelMixin` to provide a neat way of handling non-(database)-model-related permissions
  * Improved mixin documentation
  * Updated GitHub Actions

**6.5.0** (2022-09-29)
  * Added view mixin `UserInFormKwargsMixin` to pass the user to a form in a `FormView`, `CreateView` or `UpdateView`

**6.4.0** (2022-09-29)
  * Models inheriting from `CommonInfo` will automatically save the four CommonInfo fields in addition to the fields
    selected when using `update_fields` in the models save method.

**6.3.2** (2022-09-29)
  * Updated gitlab-ci for showing tests in MR

**6.3.1** (2022-09-19)
  * Updated GitHub test matrix OS

**6.3.0** (2022-09-19)
  * Integrated `flake8-bugbear` and `pyupgrade` including required code adjustments
  * Improved security vulnerability scanning
  * Updated local build and test suite to Python 3.10
  * Added `flake8-bugbear` to Quality Assurance measures
  * Added `pyupgrade` to Quality Assurance measures

**6.2.3** (2022-08-15)
  * Fixed some translations

**6.2.2** (2022-08-12)
  * Added Django 4.1 to test matrix and compatible versions

**6.2.1** (2022-08-12)
  * Improved detecting of permission mismatches in view test mixin `BaseViewPermissionTestMixin`

**6.2.0** (2022-07-13)
  * Added test case for `BaseViewPermissionTestMixin` to ensure that defined permissions exist in the database

**6.1.3** (2022-06-30)
  * Clarified docs for `GloballyVisibleQuerySet`

**6.1.2** (2022-06-30)
  * Extended docs for `BaseViewPermissionTestMixin` with limitation when using a caching wrapper

**6.1.1** (2022-06-29)
  * Fixed unittest for django<3.2

**6.1.0** (2022-06-29)
  * Added `DjangoPermissionRequiredMixin` for Django views and supporting test mixin `BaseViewPermissionTestMixin`
  * Increased minimal required bugfix version for Django 2.2
  * Updated Readme file

**6.0.0** (2022-05-19)
  * *Breaking change:* Removed `ffmpeg` helper methods `generate_video_thumbnail()` and `get_video_length()`
  * Added `CleanOnSaveMixin`
  * black and isort linting integrated
  * Added pre-commit hooks for linting

**5.14.1** (2022-04-06)
  * Dropped support for deprecated Python 3.6

**5.14.0** (2022-04-06)
  * `EmailTestService` can now filter for subjects using regular expressions

**5.13.7** (2022-03-14)
  * Fixed typo in coverage validator

**5.13.6** (2022-03-11)
  * Improved console logging for coverage validator

**5.13.5** (2022-02-28)
  * Improved motivation in class-based email docs

**5.13.4** (2022-02-28)
  * Added Script for updating mirror
  * Fixed typo in documentation

**5.13.3** (2022-02-23)
  * Added GitHub action matrix for running tests on django/python combinations
  * Updated Ambient email addresses to new domain
  * Removed django <4.0 restriction
  * Fixed tests for django 4.0

**5.13.2** (2022-02-21)
  * `CurrentUserMiddleware` bugfix, cleaning up user variable for single-threaded tests after request processing
  * Fixed version typo in changelog

**5.13.1** (2022-02-04)
  * GraphQL docs bugfix

**5.13.0** (2022-02-03)
  * Added a view which allows logging errors to Sentry normally while using Graphene.

**5.12.1** (2022-01-31)
  * Fixed bug in GitLab code coverage compare service documentation

**5.12.0** (2022-01-28)
  * Added GitLab code coverage compare service `CoverageService` with documentation

**5.11.1** (2022-01-24)
  * Added docs for `ToggleView`
  * Fixed some typos in `Readme.md` and `changelog.md`

**5.11.0** (2022-01-24)
  * Added generic `ToggleView`
  * Updated some docstrings in `formset_view_mixin`

**5.10.1** (2021-12-10)
  * Added docs about GDPR-compliant use of sentry with user data
  * Fixed some versions to make Sphinx build work again

**5.10.0** (2021-12-10)
  * Added helper method for sentry to GDPR-compliant remove sensitive user data from event
  * Updated type hints in `BaseEmailServiceFactory` init method
  * Improved docs for method `get_start_and_end_date_from_calendar_week`

**5.9.1** (2021-11-25)
  * Fixed typo in custom scrubber class logging
  * Rewrote permission manager docs and added better best practice
  * Update in email testing docs

**5.9.0** (2021-11-18)
    * Added default truncate of django session table to `AbstractScrubbingService`

**5.8.0** (2021-11-11)
    * Added `url` parameter to `RequestProviderMixin`

**5.7.4** (2021-11-08)
    * Added missing documentation about semantic database anonymisation
    * Added missing documentation about string utils
    * Added missing documentation about `get_namedtuple_choices()` helper
    * Added missing documentation about `CrispyLayoutFormMixin`
    * Added missing documentation about `ClassBasedViewTestMixin`

**5.7.3** (2021-10-22)
    * Added missing documentation about email testing
    * Updated Readme file

**5.7.2** (2021-10-21)
    * Fixed `flit` configuration

**5.7.1** (2021-10-21)
    * Setup `flit` for release management

**5.7.0** (2021-10-15)
    * Added admin mixin `DeactivatableChangeViewAdminMixin`
    * Added `response` parameter to testing middlewares

**5.6.0** (2021-09-01)
    * Extracted embedded form valid logic to separate method with super call in `_FormsetMixin`
    * Added documentation about `FormsetCreateViewMixin` and `FormsetUpdateViewMixin`

**5.5.2** (2021-08-24)
    * Added documentation about `BleacherMixin`

**5.5.1** (2021-08-24)
    * Added explicit declaration of bleacher field list attribute `BLEACH_FIELD_LIST` in `BleacherMixin`

**5.5.0** (2021-08-02)
    * Added validation for user object in `RequestProviderMixin`
    * Added link to changelog in setup.py
    * Moved minimum django version to 2.2

**5.4.0** (2021-06-28)
    * Added `__len__` and `__iter__` to EmailTestService
    * EmailTestService uses EmailTestServiceMail instances, which wrap the underlying Django mail objects, and provide
      additional assertion functions

**5.3.0** (2021-06-16)
    * Added `method` kwarg to `RequestProviderMixin.get_request()`

**5.2.2** (2021-05-27)
    * Fixed a bug in `BaseEmailService` where txt part was rendered sometimes with weird line breaks
    * Added Bugtracker link to `setup.py`

**5.2.1** (2021-05-12)
    * Translation files were missing in wheel
    * Bugfix in docs

**5.2.0** (2021-05-11)
    * Changed all translatable texts to English base version
    * Added German translation file for current translatable
    * Updated RequestProviderMixin.get_request() type hinting
    * Added documentation for database anonymisation / django-scrubber wrapper

**5.1.1** (2021-04-21)
    * Extended email attachment functionality to be able to define filename and mimetype

**5.1.0** (2021-04-20)
    * *Breaking change:* Fixed typo in `WhitelistEmailBackend.whitify_mail_adresses` method name. Method is now
      called `whitify_mail_addresses`
    * Moved assignment of `WhitelistEmailBackend` settings var to static methods to be able to overwrite them if needed
    * Added documentation about `WhitelistEmailBackend`
    * Added some type hinting to `WhitelistEmailBackend`
    * Added formset mixin `CountChildrenFormsetMixin`
    * Added djangorestframework field `RecursiveField`
    * Added `get_attachments()` method to `BaseEmailService` and extended constructor to accept a
      variable `attachment_list`

**5.0.0** (2021-03-26)
    * *Breaking change:* Moved `ReadOnlyAdmin` and `EditableOnlyAdmin` to package `model_admins.classes`
      and `ReadOnlyTabularInline` to package `model_admins.inlines` to enable better structuring of new admin components
    * Fixed some inconsistencies within `ReadOnlyAdmin`, `EditableOnlyAdmin` and `ReadOnlyTabularInline` classes
    * Added `admin.views` package containing a base crispy form, and a mixin to turn any regular django view into a nice
      and cozy django admin view
    * Added an abundance of `model_admins.mixins`: `AdminCreateFormMixin`, `AdminNoInlinesForCreateMixin`
      ,`AdminRequestInFormMixin`, `FetchParentObjectInlineMixin`, `FetchObjectMixin`, `CommonInfoAdminMixin`
    * Added `RequestProviderMixin` to easily create a dummy request in unittests
    * Added support for django 3.2 and dropped support for 2.0, 2.1 and 3.0
    * Added support for Python 3.9 and dropped support for 3.5
    * Updated test python version to 3.9

**4.2.1** (2021-03-17)
    * Added some links to setup.py for pypi
    * Added some documentation for setting up the toolbox

**4.2.0** (2021-03-12)
    * Added ``GloballyVisibleQuerySet`` including tests and documentation
    * Added ``BaseViewSetTestMixin`` for the djangorestframework plugin
    * Fixed some typos in the documentation

**4.1.2** (2021-03-05)
    * Added kwargs parameter to init-method of `BaseEmailServiceFactory`

**4.1.1** (2021-03-04)
    * Fixed a bug in the documentation

**4.1.0** (2021-02-25)
    * Added class `BaseEmailService` for easier email creation and factory `BaseEmailServiceFactory`
      for multiple (mostly personalised) emails
    * Added `html2text` as a dependency to be able to automatically process the text part of an email from the html
      template

**4.0.2** (2021-02-24)
    * Fixed a bug in ``EmailTestService.assert_body_contains()`` method to make it work for emails NOT having an HTML
      part

**4.0.1** (2021-01-29)
    * Optimised code of function `test_get_value_from_tuple_by_key_found()`
    * Added unittests for named tuple functions

**4.0.0** (2020-11-10)
    * *Breaking change:* Moved view mixin ``RequestInFormKwargsMixin`` from ``mixin.forms`` to proper place
      ``mixin.views``
    * *Breaking change:* Removed string helper function ``restore_windows1252controls()``, ``number_to_text()`` and
      ``replace_link_pattern()``
    * *Breaking change:* Removed choice converter function ``get_name_by_value()`` in favour
      of ``get_value_from_tuple_by_key()``
    * *Breaking change:* Removed date converter function ``get_seconds()`` because Python 3.6 already provides
      a `total_seconds()` method
    * *Breaking change:* Removed date converter function ``get_current_datetime()`` because django already provides
      the `timezone.now()` method
    * *Breaking change:* Removed date converter function ``diff_month()`` in favour of ``date_month_delta()``
    * *Breaking change:* Merged ``converter`` package in ``utils`` package
    * *Breaking change:* Moved view-layer-based helpers to extra requirement ``view-layer``: `_FormsetMixin`,
      `FormsetUpdateViewMixin`, `FormsetCreateViewMixin`, `CrispyLayoutFormMixin`, `CustomPermissionMixin`
      , `RequestInFormKwargsMixin`
    * Simplified code of function ``float_to_string()``
    * Added type hinting to lots of helper functions
    * Updated and restructured documentation
    * Added security check for dependencies in local pipeline
    * Removed some old python 2.7 syntax

**3.5.2** (2021-01-07)
    * Bugfix with args and kwargs in ``ReadOnlyTabularInline``

**3.5.1** (2020-11-19)
    * Bugfix with args and kwargs in ``ClassBasedViewTestMixin``

**3.5.0** (2020-11-10)
    * Merged package ``graphene-django-ai`` into this package and enabled graphql-specific installation
      with `pip install ambient_toolbox[graphql]`
    * Added some files for readthedocs.io and updated Readme

**3.4.0** (2020-10-30)
    * Moved tests out of package scope
    * Updated test python version to 3.8
    * Added tests for context manager ``TempDisconnectSignal`` with test setup

**3.3.0** (2020-10-30)
    * Merged package ``ai-drf-core`` into this package and enabled djangorestframework-specific installation
      with `pip install ambient_toolbox[drf]`
    * Added ``BaseModelSerializer`` and ``CommonInfoSerializer``
    * Incremented dependencies django and bleach to previous versions latest bugfix release

**3.2.0** (2020-10-16)
    * Added ``AbstractPermissionMixin``, ``AbstractUserSpecificQuerySet`` and ``AbstractUserSpecificManager`` abstract
      managers
    * Removed deprecated `antivir` package
    * Added Sphinx documentation setup to package

**3.1.0** (2020-10-14)
    * Added context manager ``TempDisconnectSignal`` to nicely disable model signals temporarily
    * Moved dev dependencies to ``extras_require`` in the setup file

**3.0.2** (2020-10-15)
    * Imports all utils into the modules scope
    * Re-translated some docstrings into English
    * Added tests for the `log_whodid` util function

**3.0.1** (2020-10-12)
    * Added missing ``__init__.py`` file to package mail.services

**3.0.0** (2020-09-09)
    * *Breaking change:*  Renamed package from `ai` to `ambient_toolbox` to clarify dependencies for usages
    * Finished code linting
    * Removed unused imports in antivirus util package

**2.3.0** (2020-08-07)
    * Changed `ugettext_lazy` to `gettext_lazy` to tackle django 4.0 deprecation warnings

**2.2.1** (2020-07-01)
    * Removed misleading inheritance of mixin `ClassBasedViewTestMixin` from `TestCase`

**2.2.0** (2020-07-01)
    * Added response class `CustomPermissionMixin`

**2.1.2** (2020-04-30)
    * Extended pypi documentation with classifiers

**2.1.1** (2020-04-24)
    * Refactors open calls to use context managers
    * Refactors the test setup
    * Configures coverage
    * Adds a coverage report to the CI

**2.1.0** (2020-04-20)
    * Removed password generator method `generate_password`
    * Renamed math method `round_up_to_decimal` to `round_up_decimal`
    * Added math method `round_to_decimal`
    * Updated metadata in setup.cfg

**2.0.0** (2020-04-09)
    * Dropped Python 2.x support
    * Removed explicit dependency to package `mock` and using implicit one via unittest
    * Improved linting

**1.2.14** (2020-04-06)
    * Fixed a bug with session setup in `ClassBasedViewTestMixin`

**1.2.13** (2020-04-02)
    * Added ``DELETE`` method for testing mixing `ClassBasedViewTestMixin`

**1.2.12** (2020-02-14)
    * Added CBV testing mixing `ClassBasedViewTestMixin`

**1.2.11** (2020-01-28)
    * Bugfix in documentation

**1.2.10** (2020-01-28)
    * Improved documentation

**1.2.9** (2020-01-02)
    * Extended and improved class `AbstractScrubbingService`

**1.2.8** (2019-12-13)
    * Added custom scrubber class `AbstractScrubbingService` to provide a helper for adding custom scrubbing logic for
      data anonymisation

**1.2.7** (2019-07-11)
    * Added email testing class `EmailTestService` to provide a wrapper for better email unittests

**1.2.6** (2019-07-02)
    * Added helper class `tz_today()` to provide an easy getter for a timezone-aware today

**1.2.5** (2019-06-25)
    * Added helper class `DateHelper` to provide constants to use in django's ORM lookup `__week_day`

**1.2.4** (2019-05-20)
    * More refactoring on `CurrentUserMiddleware` to make it easier to override internal functions

**1.2.3** (2019-05-20)
    * Moved `get_current_user` function inside `CurrentUserMiddleware` as a static method to enable devs to override it

**1.2.2** (2019-04-05)
    * Updated deployment documentation
    * Added markdown support to Readme file

**1.2.1** (2019-03-25)
    * Fixed bug causing `CommonInfo` middleware to not set `lastmodified_by` on object creation

**1.2.0** (2019-03-19)
    * Added `CommonInfo` middleware

**1.1.8**
    * Readonly admin classes
    * Date util functions
    * Clear cache helper

**1.1.7**
    * Settings for whitelist email services added
    * Formset mixins added

**1.1.6**
    * Modifications to antivirus field

**1.1.5**
    * Updated setup.py with newer information

**1.1.4**
    * Bleacher mixin bugfix

**1.1.3**
    * Bleacher mixin added

**< 1.1.3**
    * Ancient history :)
