import dataclasses
import importlib
import json
import os
import sys
import typing
from pathlib import Path

from django.apps import apps
from django.core.cache import cache

from ambient_toolbox.autodiscover.logger import get_logger
from ambient_toolbox.autodiscover.settings import get_autodiscover_app_base_path, get_autodiscover_cache_key
from ambient_toolbox.autodiscover.utils import unique_append_to_inner_list


# TODO: use (kw_only=True) once Python 3.9 compat was dropped
@dataclasses.dataclass
class CallableDefinition:
    """
    Projection to store registered functions in a JSON-serialisable way
    """

    module: str
    name: str


class DecoratorBasedRegistry:
    """
    Singleton for registering messages classes in.
    """

    _instance: "DecoratorBasedRegistry" = None

    def __init__(self):
        self.registry: dict = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, *, registry_group: str) -> typing.Callable:
        def decorator(decoratee) -> typing.Callable:
            # Add decoratee to dependency list
            function_definition = dataclasses.asdict(
                CallableDefinition(module=decoratee.__module__, name=decoratee.__name__)
            )

            # Add decoratee path to registry
            self.registry = unique_append_to_inner_list(
                data=self.registry, key=registry_group, value=function_definition
            )

            logger = get_logger()
            logger.debug("Registered callable '%s'", decoratee.__name__)

            # Return decoratee
            return decoratee

        return decorator

    def autodiscover(self, *, registry_group: str) -> None:
        """
        Detects message registries which have been registered via the "register_*" decorator.
        """
        # Fetch registered functions from cache, if possible
        self.registry = self._load_handlers_from_cache()

        # If functions were cached, we don't have to go through the file system (again)
        if len(self.registry) > 0:
            return

        # Project directory
        project_path = get_autodiscover_app_base_path()
        logger = get_logger()

        for app_config in apps.get_app_configs():
            app_path = Path(app_config.path).resolve()

            # If it's not a local app, we don't care
            if project_path not in app_path.parents:
                continue

            target_path = registry_group.replace(".", "/")

            try:
                # Detected python code is a single file
                if os.path.exists(app_path / f"{target_path}.py"):
                    module_path = f"{app_config.name}.{registry_group}"
                    self._force_import(module_path=module_path)

                # Detected python code is a python module
                for module in os.listdir(app_path / target_path):
                    if module[-3:] != ".py":
                        continue
                    module_name = module.replace(".py", "")
                    module_path = f"{app_config.name}.{registry_group}.{module_name}"
                    self._force_import(module_path=module_path)

            except FileNotFoundError:
                pass

        # Log to shell which functions have been detected
        logger.debug("Function autodiscovery running...")
        registration_counter = 0
        for group in self.registry.keys():
            function_list = ", ".join(str(x) for x in self.registry[group])
            logger.debug(f"* {group}: [{function_list}]")
            registration_counter += len(self.registry[group])

        logger.debug(f"{registration_counter} functions detected.\n")

        # Update cache
        cache.set(get_autodiscover_cache_key(), json.dumps(self.registry))

    def _force_import(self, *, module_path: str) -> None:
        sys_module = sys.modules.get(module_path)
        if sys_module:
            importlib.reload(sys_module)
        else:
            importlib.import_module(module_path)

        logger = get_logger()
        logger.debug(f'"{module_path}" imported.')

    def _load_handlers_from_cache(self) -> dict:
        """
        Get registered handler definitions from Django cache
        """
        cached_data = cache.get(get_autodiscover_cache_key())
        if cached_data is None:
            return {}
        return json.loads(cached_data)

    def get_registered_callables(self, *, registry_group: str) -> list[typing.Callable]:
        """
        Returns a list of Callables (functions and classes)
        """
        self.autodiscover(registry_group=registry_group)

        callables = []
        callable_definition: dict[str:str]
        for group in self.registry.keys():
            for group_data in self.registry[group]:
                callable_definition: CallableDefinition = CallableDefinition(**group_data)
                module = importlib.import_module(callable_definition.module)
                callables.append(getattr(module, callable_definition.name))

        return callables
