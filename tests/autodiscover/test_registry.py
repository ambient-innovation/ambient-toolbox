import json
from pathlib import Path
from unittest import mock

from django.core.cache import cache
from django.test import override_settings

from ambient_toolbox.autodiscover.registry import DecoratorBasedRegistry
from ambient_toolbox.autodiscover.settings import get_autodiscover_cache_key


def dummy_function(*args):
    return None


def dummy_function_2(*args):
    return None


def test_decorator_based_registry_init_regular():
    decorator_based_registry = DecoratorBasedRegistry()

    assert decorator_based_registry.registry == {}


def test_decorator_based_registry_singleton_works():
    decorator_based_registry_1 = DecoratorBasedRegistry()
    decorator_based_registry_1.registry[0] = "my_module"
    decorator_based_registry_2 = DecoratorBasedRegistry()

    assert decorator_based_registry_1 is decorator_based_registry_2
    assert decorator_based_registry_1.registry == decorator_based_registry_2.registry


def test_decorator_based_registry_register_regular():
    decorator_based_registry = DecoratorBasedRegistry()
    decorator = decorator_based_registry.register(registry_group="test")
    decorator(dummy_function)

    assert len(decorator_based_registry.registry) == 1
    assert "dummy_function" in str(decorator_based_registry.registry["test"][0])


def test_decorator_based_registry_register_second_function():
    decorator_based_registry = DecoratorBasedRegistry()
    decorator = decorator_based_registry.register(registry_group="test")
    decorator(dummy_function)
    decorator(dummy_function_2)

    assert len(decorator_based_registry.registry) == 1
    assert "dummy_function" in str(decorator_based_registry.registry["test"][0])
    assert "dummy_function_2" in str(decorator_based_registry.registry["test"][1])


def test_decorator_based_registry_register_two_groups():
    decorator_based_registry = DecoratorBasedRegistry()
    decorator = decorator_based_registry.register(registry_group="one")
    decorator(dummy_function)
    decorator = decorator_based_registry.register(registry_group="two")
    decorator(dummy_function_2)

    assert len(decorator_based_registry.registry) == 2  # noqa: PLR2004
    assert "dummy_function" in str(decorator_based_registry.registry["one"][0])
    assert "dummy_function_2" in str(decorator_based_registry.registry["two"][0])


def test_decorator_based_registry_autodiscover_target_is_python_module():
    cache.clear()

    decorator_based_registry = DecoratorBasedRegistry()
    decorator_based_registry.autodiscover(registry_group="autodiscover")

    # Assert two functions registered
    assert len(decorator_based_registry.registry) == 2  # noqa: PLR2004
    assert "testapp" in decorator_based_registry.registry.keys()
    assert "other" in decorator_based_registry.registry.keys()

    # Assert one function registered for "testapp"
    assert len(decorator_based_registry.registry["testapp"]) == 1
    assert {
        "module": "testapp.autodiscover.registered_functions",
        "name": "registered_dummy_function_testapp",
    } == decorator_based_registry.registry["testapp"][0]

    # Assert one function registered for "other"
    assert len(decorator_based_registry.registry["other"]) == 2  # noqa: PLR2004
    assert {
        "module": "testapp.autodiscover.registered_functions",
        "name": "registered_dummy_function_other",
    } == decorator_based_registry.registry["other"][0]
    assert {
        "module": "testapp.autodiscover.registered_functions",
        "name": "DummyClass",
    } == decorator_based_registry.registry["other"][1]


def test_decorator_based_registry_autodiscover_target_is_python_file():
    cache.clear()

    decorator_based_registry = DecoratorBasedRegistry()
    decorator_based_registry.autodiscover(registry_group="more_registered_functions")

    # Assert two functions registered
    assert len(decorator_based_registry.registry) == 1
    assert "no_module" in decorator_based_registry.registry.keys()

    # Assert one function registered for "testapp"
    assert len(decorator_based_registry.registry["no_module"]) == 1
    assert {
        "module": "testapp.more_registered_functions",
        "name": "even_more_registered_function",
    } == decorator_based_registry.registry["no_module"][0]


def test_decorator_based_registry_autodiscover_registry_group_contains_subpackages():
    cache.clear()

    decorator_based_registry = DecoratorBasedRegistry()
    decorator_based_registry.autodiscover(registry_group="handlers.commands")

    # Assert two functions registered
    assert len(decorator_based_registry.registry) == 1
    assert "commands" in decorator_based_registry.registry.keys()

    # Assert one function registered for "testapp"
    assert len(decorator_based_registry.registry["commands"]) == 1
    assert {
        "module": "testapp.handlers.commands.test_commands",
        "name": "my_command_handler",
    } == decorator_based_registry.registry["commands"][0]


@mock.patch("ambient_toolbox.autodiscover.registry.get_autodiscover_app_base_path", return_value=Path("/some/path"))
def test_decorator_based_registry_autodiscover_no_local_apps(*args):
    cache.clear()

    decorator_based_registry = DecoratorBasedRegistry()
    decorator_based_registry.autodiscover(registry_group="autodiscover")

    assert len(decorator_based_registry.registry) == 0


@mock.patch("importlib.import_module")
@mock.patch("importlib.reload")
def test_decorator_based_registry_autodiscover_caching_avoid_importing_again(
    mocked_reload_module, mocked_import_module
):
    cache.set(
        get_autodiscover_cache_key(),
        json.dumps({"testapp": ["dummy_function_testapp"], "other": ["dummy_function_other"]}),
    )

    decorator_based_registry = DecoratorBasedRegistry()
    decorator_based_registry.autodiscover(registry_group="autodiscover")

    assert mocked_reload_module.call_count == 0
    assert mocked_import_module.call_count == 0


def test_decorator_based_registry_autodiscover_load_handlers_from_cache_regular(*args):
    cache.set(
        get_autodiscover_cache_key(),
        json.dumps({"testapp": ["dummy_function_testapp"], "other": ["dummy_function_other"]}),
    )

    decorator_based_registry = DecoratorBasedRegistry()
    registered_callables = decorator_based_registry._load_handlers_from_cache()

    assert len(registered_callables) == 2  # noqa: PLR2004


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
def test_decorator_based_registry_autodiscover_load_handlers_from_cache_dummy_cache(*args):
    decorator_based_registry = DecoratorBasedRegistry()
    registered_callables = decorator_based_registry._load_handlers_from_cache()

    assert len(registered_callables) == 0


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
def test_get_registered_callables_found_and_executable():
    decorator_based_registry = DecoratorBasedRegistry()
    callables = decorator_based_registry.get_registered_callables(registry_group="autodiscover")

    assert len(callables) == 3  # noqa: PLR2004
    assert callables[0]() == "testapp"
    assert callables[1]() == "other"
    assert str(callables[2]()) == "DummyClass"
