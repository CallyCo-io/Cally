from functools import update_wrapper

import click

from . import CallyCommandClass, CallyConfig, config_types, mixins
from .options import CALLY_SERVICE_OPTIONS


class CallyStackServiceConfig(
    CallyConfig[config_types.CallyStackService], mixins.CallyService
):
    CALLY_TYPE = config_types.CallyStackService

    @property
    def _settings_kwargs(self) -> dict:
        return {
            'loaders': ['cally.cli.config.loaders.service'],
            'cally_env': self.environment,
            'cally_service': self.service,
        }


class CallyStackServiceConfigContext(click.Context):
    def __init__(self, *args, **kwargs) -> None:
        if kwargs.get('obj', None) is None:
            kwargs.update(obj=CallyStackServiceConfig())
        super().__init__(*args, **kwargs)


def CallyStackServiceCommand():  # noqa: N802
    class CallyStackServiceCommandClass(CallyCommandClass):
        context_class = CallyStackServiceConfigContext
        default_cally_options = CALLY_SERVICE_OPTIONS

    return CallyStackServiceCommandClass
