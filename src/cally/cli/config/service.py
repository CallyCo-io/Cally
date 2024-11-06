import click

from . import CallyCommandClass, CallyConfig, config_types, mixins
from .options import CALLY_SERVICE_OPTIONS


class CallyServiceConfig(CallyConfig[config_types.CallyService], mixins.CallyService):
    CALLY_TYPE = config_types.CallyService

    @property
    def _settings_kwargs(self) -> dict:
        return {
            'loaders': ['cally.cli.config.loaders.service'],
            'cally_env': self.environment,
            'cally_service': self.service,
        }


class CallyServiceConfigContext(click.Context):
    def __init__(self, *args, **kwargs) -> None:
        if kwargs.get('obj', None) is None:
            kwargs.update(obj=CallyServiceConfig())
        super().__init__(*args, **kwargs)


def CallyServiceCommand():  # noqa: N802
    class CallyServiceCommandClass(CallyCommandClass):
        context_class = CallyServiceConfigContext
        default_cally_options = CALLY_SERVICE_OPTIONS

    return CallyServiceCommandClass
