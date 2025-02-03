from ambient_toolbox.autodiscover import function_registry


@function_registry.register_function(registry_group="no_module")
def even_more_registered_function():
    pass
