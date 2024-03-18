import click

from ..config.types import CallyStackService
from ..tools import terraform


@click.group()
def tf() -> None:
    pass


@click.command(name='print')
# TODO: Load this by default from config
@click.option('--stack-name')
@click.option('--stack-type')
def print_template(stack_name: str, stack_type: str):
    service = CallyStackService(name=stack_name, environment='test')
    with terraform.Action(stack_type=stack_type, service=service) as action:
        click.secho(action.print())


tf.add_command(print_template)
