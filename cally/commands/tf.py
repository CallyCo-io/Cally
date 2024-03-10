import click

from ..tools import terraform


@click.group()
def tf() -> None:
    pass


@click.command(name='print')
@click.option('--stack-name')
@click.option('--stack-type')
def print_template(stack_name: str, stack_type: str):
    with terraform.Action(stack_name=stack_name, stack_type=stack_type) as action:
        click.secho(action.print())


tf.add_command(print_template)
