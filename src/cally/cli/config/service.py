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
    """This can be applied to the 'cls' kwarg of a click.command decorator. It
    will make all service options available to the decorated command. Best combined
    with the pass object decorator for convenient access to the CallyServiceConfig
    object.

    Example usage::

        @click.command(name='print', cls=CallyServiceCommand())
        @click.pass_obj
        def example(service: CallyServiceConfig):
            click.echo(service.config.name)

    """

    class CallyServiceCommandClass(CallyCommandClass):
        context_class = CallyServiceConfigContext
        default_cally_options = CALLY_SERVICE_OPTIONS

    return CallyServiceCommandClass
