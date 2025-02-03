from ambient_toolbox.autodiscover import function_registry


@function_registry.register_function(registry_group="commands")
def my_command_handler():
    pass
