from dataclasses import fields
from functools import update_wrapper
from pathlib import Path
from typing import Optional, Union

import click
from dynaconf import Dynaconf

from . import CallyConfig, ctx_callback
from . import types as cally_types
from .validators import BASE_CALLY_CONFIG


class CallyEnvironmentConfig(CallyConfig):
    _environment: Optional[str] = None
    _service: Optional[str] = None
    _settings: Dynaconf
    loader = 'cally.cli.config.loaders.environment'
    cally_type = 'CallyEnvironment'

    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file

    @property
    def environment(self) -> Optional[str]:
        return self._environment

    @environment.setter
    def environment(self, value: str):
        self._environment = value

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


def environment_options(func):
    """This decorator, can be used on any custom commands where you expect
    an environment to be set.
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
    ]
    for option in reversed(options):
        func = option(func)
    return func


def pass_stack_obj(f):
    @click.pass_obj
    def new_func(obj: CallyEnvironmentConfig, *args, **kwargs):
        return f(obj, *args, **kwargs)

    return update_wrapper(new_func, f)
