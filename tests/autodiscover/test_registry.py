import json
from pathlib import Path
from unittest import mock

from django.core.cache import cache
from django.test import override_settings

from ambient_toolbox.autodiscover.registry import FunctionRegistry
from ambient_toolbox.autodiscover.settings import get_autodiscover_cache_key


def dummy_function(*args):
    return None


def dummy_function_2(*args):
    return None


def test_function_registry_init_regular():
    function_registry = FunctionRegistry()

    assert function_registry.registry == {}


def test_function_registry_singleton_works():
    function_registry_1 = FunctionRegistry()
    function_registry_1.registry[0] = "my_module"
    function_registry_2 = FunctionRegistry()

    assert function_registry_1 is function_registry_2
    assert function_registry_1.registry == function_registry_2.registry


def test_function_registry_register_function_regular():
    function_registry = FunctionRegistry()
    decorator = function_registry.register_function(registry_group="test")
    decorator(dummy_function)

    assert len(function_registry.registry) == 1
    assert "dummy_function" in str(function_registry.registry["test"][0])


def test_function_registry_register_function_second_function():
    function_registry = FunctionRegistry()
    decorator = function_registry.register_function(registry_group="test")
    decorator(dummy_function)
    decorator(dummy_function_2)

    assert len(function_registry.registry) == 1
    assert "dummy_function" in str(function_registry.registry["test"][0])
    assert "dummy_function_2" in str(function_registry.registry["test"][1])


def test_function_registry_register_function_two_groups():
    function_registry = FunctionRegistry()
    decorator = function_registry.register_function(registry_group="one")
    decorator(dummy_function)
    decorator = function_registry.register_function(registry_group="two")
    decorator(dummy_function_2)

    assert len(function_registry.registry) == 2  # noqa: PLR2004
    assert "dummy_function" in str(function_registry.registry["one"][0])
    assert "dummy_function_2" in str(function_registry.registry["two"][0])


def test_function_registry_autodiscover_target_is_python_module():
    cache.clear()

    function_registry = FunctionRegistry()
    function_registry.autodiscover(registry_group="autodiscover")

    # Assert two functions registered
    assert len(function_registry.registry) == 2  # noqa: PLR2004
    assert "testapp" in function_registry.registry.keys()
    assert "other" in function_registry.registry.keys()

    # Assert one function registered for "testapp"
    assert len(function_registry.registry["testapp"]) == 1
    assert {
        "module": "testapp.autodiscover.registered_functions",
        "name": "registered_dummy_function_testapp",
    } == function_registry.registry["testapp"][0]

    # Assert one function registered for "other"
    assert len(function_registry.registry["other"]) == 1
    assert {
        "module": "testapp.autodiscover.registered_functions",
        "name": "registered_dummy_function_other",
    } == function_registry.registry["other"][0]


def test_function_registry_autodiscover_target_is_python_file():
    cache.clear()

    function_registry = FunctionRegistry()
    function_registry.autodiscover(registry_group="more_registered_functions")

    # Assert two functions registered
    assert len(function_registry.registry) == 1
    assert "no_module" in function_registry.registry.keys()

    # Assert one function registered for "testapp"
    assert len(function_registry.registry["no_module"]) == 1
    assert {
        "module": "testapp.more_registered_functions",
        "name": "even_more_registered_function",
    } == function_registry.registry["no_module"][0]


def test_function_registry_autodiscover_target_name_contains_subpackages():
    cache.clear()

    function_registry = FunctionRegistry()
    function_registry.autodiscover(registry_group="handlers.commands")

    # Assert two functions registered
    assert len(function_registry.registry) == 1
    assert "commands" in function_registry.registry.keys()

    # Assert one function registered for "testapp"
    assert len(function_registry.registry["commands"]) == 1
    assert {
        "module": "testapp.handlers.commands.test_commands",
        "name": "my_command_handler",
    } == function_registry.registry["commands"][0]


@mock.patch("ambient_toolbox.autodiscover.registry.get_autodiscover_app_base_path", return_value=Path("/some/path"))
def test_function_registry_autodiscover_no_local_apps(*args):
    cache.clear()

    function_registry = FunctionRegistry()
    function_registry.autodiscover(registry_group="autodiscover")

    assert len(function_registry.registry) == 0


@mock.patch("importlib.import_module")
@mock.patch("importlib.reload")
def test_function_registry_autodiscover_caching_avoid_importing_again(mocked_reload_module, mocked_import_module):
    cache.set(
        get_autodiscover_cache_key(),
        json.dumps({"testapp": ["dummy_function_testapp"], "other": ["dummy_function_other"]}),
    )

    function_registry = FunctionRegistry()
    function_registry.autodiscover(registry_group="autodiscover")

    assert mocked_reload_module.call_count == 0
    assert mocked_import_module.call_count == 0


def test_function_registry_autodiscover_load_handlers_from_cache_regular(*args):
    cache.set(
        get_autodiscover_cache_key(),
        json.dumps({"testapp": ["dummy_function_testapp"], "other": ["dummy_function_other"]}),
    )

    function_registry = FunctionRegistry()
    registered_functions = function_registry._load_handlers_from_cache()

    assert len(registered_functions) == 2  # noqa: PLR2004


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
def test_function_registry_autodiscover_load_handlers_from_cache_dummy_cache(*args):
    function_registry = FunctionRegistry()
    registered_functions = function_registry._load_handlers_from_cache()

    assert len(registered_functions) == 0


def test_get_registered_callables_found_and_executable():
    function_registry = FunctionRegistry()
    callables = function_registry.get_registered_callables(target_name="autodiscover")

    assert len(callables) == 2  # noqa: PLR2004
    assert callables[0]() == "testapp"
    assert callables[1]() == "other"
