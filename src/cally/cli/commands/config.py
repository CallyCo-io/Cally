import click
import yaml

from ..config.environment import CallyEnvironmentCommand, CallyEnvironmentConfig
from ..config.service import CallyServiceCommand, CallyServiceConfig


@click.group()
def config() -> None:
    pass


@click.command(cls=CallyServiceCommand())
@click.pass_obj
def print_service(config: CallyServiceConfig):
    """Prints the service config as YAML"""
    click.secho(yaml.dump(config.settings.to_dict()))


@click.command(cls=CallyEnvironmentCommand())
@click.pass_obj
def print_services(config: CallyEnvironmentConfig):
    """Prints all the services in an environment config as YAML"""
    click.secho(yaml.dump(config.settings.to_dict()))


config.add_command(print_service)
config.add_command(print_services)
