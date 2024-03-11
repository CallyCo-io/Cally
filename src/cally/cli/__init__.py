import pkgutil
from importlib import import_module
from pathlib import Path
from typing import List

import click
from click import Group

from . import commands as builtin_commands
from ._version import VERSION as __version__  # noqa: N811


# TODO: Investigate the lazy loader as this might become quite slow
# https://click.palletsprojects.com/en/8.1.x/complex/#defining-the-lazy-group
def get_commands() -> List:
    """
    Convenience method for collecting all available commands
    """
    groups = {}
    for _, name, _is_pkg in pkgutil.walk_packages(builtin_commands.__path__):
        full_name = f'{builtin_commands.__name__}.{name}'
        module = import_module(full_name)
        for sub_module in dir(module):
            attr = getattr(module, sub_module)
            if isinstance(attr, Group):
                groups.update({name: attr})

    return [val for (_, val) in groups.items() if isinstance(val, click.core.Command)]


@click.group()
@click.option(
    '--core-config',
    type=click.Path(path_type=Path),
    default=Path(Path.home(), '.config', 'cally.yaml'),
    envvar='CALLY_CORE_CONFIG',
    help='Path to the core config file',
)
@click.option(
    '--project-config',
    type=click.Path(path_type=Path),
    default=Path(Path.cwd(), '.cally.yaml'),
    envvar='CALLY_PROJECT_CONFIG',
    help='Path to the project config file',
)
@click.version_option(__version__)
@click.pass_context
def cally(
    ctx: click.Context,  # noqa: ARG001
    core_config: click.Path,  # noqa: ARG001
    project_config: click.Path,  # noqa: ARG001
) -> None:
    """
    Top level click command group for Cally
    """


for command in get_commands():
    cally.add_command(command)
