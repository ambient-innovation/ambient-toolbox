from ambient_toolbox.autodiscover import function_registry


@function_registry.register_function(registry_group="testapp")
def registered_dummy_function_testapp():
    return "testapp"


@function_registry.register_function(registry_group="other")
def registered_dummy_function_other():
    return "other"


@function_registry.register_function(registry_group="other")
class DummyClass:
    pass
