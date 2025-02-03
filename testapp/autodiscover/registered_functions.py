from ambient_toolbox.autodiscover import function_registry


@function_registry.register_function(registry_group="testapp")
def registered_dummy_function_testapp():
    pass


@function_registry.register_function(registry_group="other")
def registered_dummy_function_other():
    pass
