import click

from ..tools.provider import ProviderBuilder


@click.group()
def provider() -> None:
    pass


@click.command()
@click.option('--source', default='hashicorp')
@click.option('--provider', required=True)
@click.option('--version', required=True)
def build(source: str, provider: str, version: str):
    click.secho(f'Generating {provider} ({version}) provider')
    ProviderBuilder(source=source, provider=provider, version=version).build()


provider.add_command(build)
