from contextlib import suppress
from importlib import import_module
from pathlib import Path
from pkgutil import walk_packages
from typing import List

import click
from click import Group

from ._version import VERSION as __version__  # noqa: N811
from .config import CallyConfig


# TODO: Investigate the lazy loader as this might become quite slow
# https://click.palletsprojects.com/en/8.1.x/complex/#defining-the-lazy-group
def get_commands(package_name: str) -> List:
    """
    Convenience method for collecting all available commands
    """
    groups = {}
    package = import_module(package_name)
    for _, name, _is_pkg in walk_packages(package.__path__):
        full_name = f'{package.__name__}.{name}'
        module = import_module(full_name)
        for sub_module in dir(module):
            attr = getattr(module, sub_module)
            if isinstance(attr, Group):
                groups.update({name: attr})

    return [val for (_, val) in groups.items() if isinstance(val, click.core.Command)]


@click.group()
@click.option(
    '--config',
    type=click.Path(path_type=Path),
    default=Path(Path.cwd(), 'cally.yaml'),
    envvar='CALLY_CONFIG',
    help='Path to the project config file',
)
@click.version_option(__version__)
@click.pass_context
def cally(ctx: click.Context, config: Path) -> None:
    """
    Top level click command group for Cally
    """
    ctx.obj = CallyConfig(config_file=config)


commands = get_commands('cally.cli.commands')
with suppress(ModuleNotFoundError):
    commands.extend(get_commands('cally.idp.commands'))
for command in commands:
    cally.add_command(command)
