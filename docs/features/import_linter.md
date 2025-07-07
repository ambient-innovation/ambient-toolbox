# Import linter

The [import-linter](https://pypi.org/project/import-linter/) package checks import based on rules called "contracts".
This comes in quite handy when using a layered architecture. But it also enables the CI to ensure that certain apps are
imported only in one direction.

## "Mono-app" approach

A common pattern for Django is the "mono-app" approach. This means that all relevant business logic in your project
lives within one Django app. Code that is independent of this code, like generic utils, translation feature, etc. might
live in other Django apps. But to ensure a clean architecture and avoid creating a big ball of mud, the import-linter
contracts can ensure that these non-business-logic apps are agnostic of the business logic part and all other apps.

Since new apps can be created quite easily and creating these contracts is a little tedious, this package provides two
helpers.

### Updating contracts

When you add a new Django app, run this command to update your contracts in your `pyproject.toml`:

> python manage.py update_import_linter_contracts

### Valdating contracts

Since it's quite easy to forget that these contracts exist, this package provides a validation script which you can run
in your CI/CD to ensure that your contracts are up to date.

> python manage.py validate_import_linter_contracts

## Configuration

For these features, a little bit of setup is required.

````python
# Global Django settings.py

# All apps which should be independent of one another
TOOLBOX_IMPORT_LINTER_ROOT_PACKAGES = CUSTOM_LOCAL_APPS
# Apps which contain business logic
TOOLBOX_IMPORT_LINTER_BUSINESS_LOGIC_APPS = ["myproject"]
# Exclude apps which are not relevant for the contracts
TOOLBOX_IMPORT_LINTER_BLOCKLISTED_APPS = ["deprecated_app"]
# List of all local Django apps
TOOLBOX_IMPORT_LINTER_LOCAL_APPS = CUSTOM_LOCAL_APPS
# Path to your pyproject toml file, defaults to having a pyproject.toml in your base directory
TOOLBOX_IMPORT_LINTER_PATH_TO_TOML = Path("path/to/pyproject.toml")
````
