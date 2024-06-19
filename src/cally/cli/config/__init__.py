from dataclasses import fields
from functools import update_wrapper
from pathlib import Path
from typing import Optional, Union

import click
from dynaconf import Dynaconf

from . import types as cally_types
from .validators import BASE_CALLY_CONFIG


class CallyConfig:
    config_file: Path
    loader: str
    cally_type: str
    _environment: Optional[str] = None
    _service: Optional[str] = None
    _settings: Dynaconf

    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file
        self.loader = 'cally.cli.config.loaders.service'
        self.cally_type = 'CallyService'

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

    @property
    def settings(self):
        if getattr(self, '_settings', None) is None:
            self._settings = Dynaconf(
                environments=False,
                envvar_prefix='CALLY',
                root_path=Path().cwd(),
                settings_file=self.config_file,
                merge_enabled=True,
                core_loaders=[],
                loaders=[
                    self.loader,
                ],
                validators=BASE_CALLY_CONFIG,
                cally_env=self.environment,
                cally_service=self.service,
            )
        return self._settings

    def as_dataclass(
        self,
    ) -> Union[cally_types.CallyService, cally_types.CallyEnvironment]:
        cls = getattr(cally_types, self.cally_type)
        items = {
            x.name: getattr(self.settings, x.name)
            for x in fields(cls)
            if x.name in self.settings
        }
        return cls(**items)


def ctx_callback(
    ctx: click.Context, param: click.Parameter, value: Union[str, int]
) -> Union[str, int]:
    setattr(ctx.obj, str(param.name), value)
    return value


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
