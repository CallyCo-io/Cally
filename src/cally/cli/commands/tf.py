from pathlib import Path

import click

from ..config.service import CallyServiceConfig, pass_stack_obj, service_options
from ..tools import terraform


@click.group()
def tf() -> None:
    pass


@click.command(name='print')
@service_options
@pass_stack_obj
def print_template(config: CallyServiceConfig):
    with terraform.Action(service=config.as_dataclass()) as action:
        click.secho(action.print())


@click.command(name='write')
@click.option(
    '--output',
    type=click.Path(path_type=Path),
    default=Path(Path.cwd(), 'cdk.tf.json'),
    help='Output path for the terraform json',
)
@service_options
@pass_stack_obj
def write_template(config: CallyServiceConfig, output: Path):
    with terraform.Action(service=config.as_dataclass()) as action:
        output.write_text(action.print())
        click.secho(f'Template written to {output}')


tf.add_command(print_template)
tf.add_command(write_template)
