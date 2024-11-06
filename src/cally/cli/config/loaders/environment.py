from pathlib import Path

import yaml
from dynaconf import LazySettings

from . import envvar_helper, mixin_helper

try:
    from cally.idp.defaults import DEFAULTS as IDP_DEFAULTS  # type: ignore
except ModuleNotFoundError:
    IDP_DEFAULTS: dict = {}  # type: ignore[no-redef]


def load(obj: LazySettings, *args, **kwargs) -> None:  # noqa: ARG001
    """
    Load a cally yaml file, with a resolution order of defaults, environment
    defaults, service, then environment variables.

    cally.yml
    ```yaml
    defaults:
      providers:
        example:
          foo: bar
    dev:
      defaults:
        providers:
          random:
            alias: cats
      services:
        example-service:
          stack_vars:
            foo: bar
    """
    config_file = Path(obj.settings_file_for_dynaconf)
    loaded = {}
    if config_file.exists():
        loaded = yaml.safe_load(config_file.read_text())

    # Defaults
    obj.update(IDP_DEFAULTS)
    obj.update(loaded.get('defaults', {}))
    if obj.cally_env is not None:
        obj.update(environment=obj.cally_env)
        obj.update(loaded.get(obj.cally_env, {}).get('defaults', {}))

    if obj.cally_env:
        services = loaded.get(obj.cally_env, {}).get('services', {})
        for service, config in services.items():
            obj.update({'services': {service: config}})
            service_obj = obj.get('services', {}).get(service, {})
            mixin_helper(service_obj, loaded, config)

    # Process Env Vars
    envvar_helper(obj)
