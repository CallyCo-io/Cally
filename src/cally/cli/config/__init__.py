from pathlib import Path
from typing import Callable, ClassVar, Generic, List, Optional, TypeVar

import click
from dynaconf import Dynaconf

from . import config_types
from .options import CALLY_CONFIG_OPTIONS
from .validators import BASE_CALLY_CONFIG

T = TypeVar(
    "T",
    config_types.CallyEnvironment,
    config_types.CallyProject,
    config_types.CallyService,
    config_types.CallyStackService,
)


class CallyConfig(Generic[T]):
    CALLY_TYPE: ClassVar[Callable]
    _config_file: Path
    _config: T
    _settings: Dynaconf

    @property
    def config_file(self) -> Optional[Path]:
        return self._config_file

    @config_file.setter
    def config_file(self, value: Path):
        self._config_file = value

    @property
    def _settings_kwargs(self) -> dict:
        return {'loaders': []}

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
                validators=BASE_CALLY_CONFIG,
                **self._settings_kwargs,
            )
        return self._settings

    @property
    def config(
        self,
    ) -> T:
        if getattr(self, '_config', None) is None:
            self._config = self.CALLY_TYPE(
                **config_types.filter_dataclass_props(self.settings, self.CALLY_TYPE)
            )
        return self._config


class CallyConfigContext(click.Context):
    def __init__(self, *args, **kwargs) -> None:
        if kwargs.get('obj', None) is None:
            kwargs.update(obj=CallyConfig())
        super().__init__(*args, **kwargs)


class CallyCommandClass(click.Command):
    context_class = CallyConfigContext
    default_cally_options: List[click.Option] = CALLY_CONFIG_OPTIONS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.extend(self.default_cally_options)


def CallyCommand():  # noqa: N802
    return CallyCommandClass
