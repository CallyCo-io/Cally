from pathlib import Path
from types import ModuleType
from typing import List

import click

from . import commands as builtin_commands
from ._version import VERSION


def get_commands(class_obj: ModuleType) -> List:
    """
    Convenience method for collecting all available commands
    """
    return [
        val
        for (key, val) in vars(class_obj).items()
        if isinstance(val, click.core.Command)
    ]


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
@click.version_option(VERSION)
@click.pass_context
def cally(
    ctx: click.Context,  # noqa: ARG001
    core_config: click.Path,  # noqa: ARG001
    project_config: click.Path,  # noqa: ARG001
) -> None:
    """
    Top level click command group for Cally
    """


for command in get_commands(builtin_commands):
    cally.add_command(command)
