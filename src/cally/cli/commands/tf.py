import click

from ..config import CallyConfig, service_options
from ..tools import terraform


@click.group()
def tf() -> None:
    pass


@click.command(name='print')
@service_options
@click.pass_obj
def print_template(config: CallyConfig):
    with terraform.Action(service=config.as_dataclass('CallyStackService')) as action:
        click.secho(action.print())


tf.add_command(print_template)
