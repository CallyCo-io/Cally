import click

from . import CallyCommandClass, CallyConfig, config_types, mixins
from .options import CALLY_ENVIRONMENT_OPTIONS


class CallyEnvironmentConfig(
    CallyConfig[config_types.CallyEnvironment], mixins.CallyEnvironment
):
    CALLY_TYPE = config_types.CallyEnvironment

    @property
    def _settings_kwargs(self) -> dict:
        return {
            'loaders': ['cally.cli.config.loaders.environment'],
            'cally_env': self.environment,
        }


class CallyEnvironmentConfigContext(click.Context):
    def __init__(self, *args, **kwargs) -> None:
        if kwargs.get('obj', None) is None:
            kwargs.update(obj=CallyEnvironmentConfig())
        super().__init__(*args, **kwargs)


def CallyEnvironmentCommand():  # noqa: N802
    class CallyEnvironmentCommandClass(CallyCommandClass):
        context_class = CallyEnvironmentConfigContext
        default_cally_options = CALLY_ENVIRONMENT_OPTIONS

    return CallyEnvironmentCommandClass
