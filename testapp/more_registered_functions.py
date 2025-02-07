from ambient_toolbox.autodiscover import decorator_based_registry


@decorator_based_registry.register(registry_group="no_module")
def even_more_registered_function():
    pass
