import click


@click.group()
def example() -> None:
    pass


@click.command()
@click.argument('name')
def hello(name: str):
    click.secho(f'Hello {name}')


example.add_command(hello)
