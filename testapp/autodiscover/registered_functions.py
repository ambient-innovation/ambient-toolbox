from ambient_toolbox.autodiscover import decorator_based_registry


@decorator_based_registry.register(registry_group="testapp")
def registered_dummy_function_testapp():
    return "testapp"


@decorator_based_registry.register(registry_group="other")
def registered_dummy_function_other():
    return "other"


@decorator_based_registry.register(registry_group="other")
class DummyClass:
    def __str__(self) -> str:
        return "DummyClass"
