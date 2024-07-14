import click
import yaml

from ..config.service import CallyServiceConfig, service_options


@click.group()
def config() -> None:
    pass


@click.command()
@service_options
@click.pass_obj
def print_service(config: CallyServiceConfig):
    """Prints the service config as YAML"""
    click.secho(yaml.dump(config.settings.to_dict()))


config.add_command(print_service)
