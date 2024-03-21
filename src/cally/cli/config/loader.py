from pathlib import Path

import yaml
from dynaconf import LazySettings

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

    # Service
    if obj.cally_service is not None:
        obj.update(name=obj.cally_service)
    if all([obj.cally_env, obj.cally_service]):
        service = (
            loaded.get(obj.cally_env, {}).get('services', {}).get(obj.cally_service, {})
        )
        if service is None:
            service = {}
        mixins = service.pop('mixins', [])
        # Resolution Order: Global Mixins, Env Mixins, Service
        # The last to be loaded wins.
        for mixin in [x.strip() for x in mixins if len(x.strip()) > 0]:
            obj.update(loaded.get('mixins', {}).get(mixin, {}))
            obj.update(loaded.get(obj.cally_env, {}).get('mixins', {}).get(mixin, {}))
        obj.update(service)

    # Environment Variables
    prefix: str = obj.envvar_prefix_for_dynaconf
    remove = len(prefix) + 1  # PREFIX_ lenth
    for key, val in obj.environ.items():
        if not key.startswith(prefix):
            continue
        if key in {f'{prefix}_SERVICE', f'{prefix}_ENVIRONMENT'}:
            continue
        obj.update({key[remove:].lower(): val})

    # Clear out Service/Environment
    obj.unset(f'{prefix}_ENV')
    obj.unset(f'{prefix}_SERVICE')
