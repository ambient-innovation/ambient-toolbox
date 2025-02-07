from ambient_toolbox.autodiscover import decorator_based_registry


@decorator_based_registry.register(registry_group="commands")
def my_command_handler():
    pass
