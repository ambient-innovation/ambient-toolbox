from importlib import import_module

from django.conf import settings
from django.core.checks import Warning  # noqa: A004


def check_backend_env_variables(**kwargs) -> list[Warning]:
    """
    Check all Django settings with "_BACKEND" suffix to ensure they point to importable paths.
    """
    warnings = []

    # Scan all Django settings
    for setting_name in dir(settings):
        # Skip private/magic attributes
        if setting_name.startswith("_"):
            continue

        # Check if the setting ends with "_BACKEND"
        if not setting_name.endswith("_BACKEND"):
            continue

        # Get the setting value
        setting_value = getattr(settings, setting_name)

        # Check if the value is a string and looks like a dot-notation path
        if not isinstance(setting_value, str) or not setting_value:
            continue

        # Skip if it doesn't look like a Python path (e.g., contains spaces, special chars, etc.)
        if not is_valid_python_path(path=setting_value):
            continue

        # Try to import the path
        try:
            module_path, _, class_name = setting_value.rpartition(".")

            if not module_path:
                # No dot in the path, try to import it as a module
                import_module(setting_value)
            else:
                # Import the module and check if the class exists
                module = import_module(module_path)
                if not hasattr(module, class_name):
                    warnings.append(
                        Warning(
                            f"Setting '{setting_name}' points to '{setting_value}', "
                            f"but class '{class_name}' does not exist in module '{module_path}'.",
                            hint=f"Check that the class name is correct in the path '{setting_value}'.",
                            id="ambient_toolbox.W005",
                        )
                    )
        except ModuleNotFoundError as e:
            warnings.append(
                Warning(
                    f"Setting '{setting_name}' points to '{setting_value}', but the module could not be imported: {e}",
                    hint="Ensure the module path is correct and the module is installed.",
                    id="ambient_toolbox.W006",
                )
            )
        except ImportError as e:
            warnings.append(
                Warning(
                    f"Setting '{setting_name}' points to '{setting_value}', but an error occurred while importing: {e}",
                    hint="Check the path and ensure it's a valid Python import path.",
                    id="ambient_toolbox.W007",
                )
            )

    return warnings


def is_valid_python_path(*, path: str) -> bool:
    """
    Check if a string looks like a valid Python import path.
    """
    if not path:
        return False

    # Should not start or end with a dot
    if path.startswith(".") or path.endswith("."):
        return False

    # Split by dots and check each part is a valid Python identifier
    parts = path.split(".")
    return all(part and part.isidentifier() for part in parts)
