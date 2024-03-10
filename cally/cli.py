from pathlib import Path

import click

from . import __version__


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
    ctx: click.Context, core_config: click.Path, project_config: click.Path
) -> None:
    """
    Top level click command group for Cally
    """
