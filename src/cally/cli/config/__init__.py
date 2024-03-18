from pathlib import Path
from typing import Optional, Union

import click
from dynaconf import Dynaconf  # type: ignore


class CallyConfig:
    config_file: Path
    _environment: Optional[str] = None
    _service: Optional[str] = None
    _settings: Dynaconf

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
                    'cally.cli.config.loader',
                ],
                cally_env=self.environment,
                cally_service=self.service,
            )
        return self._settings


def ctx_callback(
    ctx: click.Context, param: click.Parameter, value: Union[str, int]
) -> Union[str, int]:
    setattr(ctx.obj, str(param.name), value)
    return value


def service_options(func):
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
