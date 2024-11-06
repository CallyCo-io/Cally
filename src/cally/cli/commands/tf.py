from pathlib import Path

import click

from ..config.terraform_service import CallyStackServiceCommand, CallyStackServiceConfig
from ..tools import terraform


@click.group()
def tf() -> None:
    pass


@click.command(name='print', cls=CallyStackServiceCommand())
@click.pass_obj
def print_template(config: CallyStackServiceConfig):
    with terraform.Action(service=config.config) as action:
        click.secho(action.print())


@click.command(name='write')
@click.option(
    '--output',
    type=click.Path(path_type=Path),
    default=Path(Path.cwd(), 'cdk.tf.json'),
    help='Output path for the terraform json',
)
@click.pass_obj
def write_template(config: CallyStackServiceConfig, output: Path):
    with terraform.Action(service=config.config) as action:
        output.write_text(action.print())
        click.secho(f'Template written to {output}')


tf.add_command(print_template)
tf.add_command(write_template)
