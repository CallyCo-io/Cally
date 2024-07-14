from functools import update_wrapper
from pathlib import Path
from typing import Optional

import click
from dynaconf import Dynaconf

from . import CallyConfig, ctx_callback


class CallyServiceConfig(CallyConfig):
    _environment: Optional[str] = None
    _service: Optional[str] = None
    _settings: Dynaconf
    loader = 'cally.cli.config.loaders.service'
    cally_type = 'CallyService'

    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file

    @property
    def environment(self) -> Optional[str]:
        return self._environment

    @environment.setter
    def environment(self, value: str):
        self._environment = value

    @property
    def service(self) -> Optional[str]:
        return self._service

    @service.setter
    def service(self, value: str):
        self._service = value


def service_options(func):
    """This decorator, can be used on any custom commands where you expect
    a service and environment to be set.
    """
    options = [
        click.option(
            '--environment',
            envvar='CALLY_ENVIRONMENT',
            expose_value=False,
            required=True,
            help='Environment to operate within',
            callback=ctx_callback,
        ),
        click.option(
            '--service',
            envvar='CALLY_SERVICE',
            expose_value=False,
            required=True,
            help='Service name to retrieve config details',
            callback=ctx_callback,
        ),
    ]
    for option in reversed(options):
        func = option(func)
    return func


def pass_stack_obj(f):
    @click.pass_obj
    def new_func(obj: CallyConfig, *args, **kwargs):
        obj.cally_type = 'CallyStackService'
        return f(obj, *args, **kwargs)

    return update_wrapper(new_func, f)
