from dynaconf import LazySettings


def mixin_helper(obj: LazySettings, loaded: dict, service: dict) -> None:
    mixins = service.pop('mixins', [])
    # Resolution Order: Global Mixins, Env Mixins, Service
    # The last to be loaded wins.
    for mixin in [x.strip() for x in mixins if len(x.strip()) > 0]:
        obj.update(loaded.get('mixins', {}).get(mixin, {}))
        obj.update(loaded.get(obj.cally_env, {}).get('mixins', {}).get(mixin, {}))
    obj.update(service)


def envvar_helper(obj: LazySettings) -> None:
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
