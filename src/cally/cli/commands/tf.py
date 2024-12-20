import sys
from pathlib import Path
from typing import Tuple

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


@click.command(name='write', cls=CallyStackServiceCommand())
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


@click.command(
    name='run',
    cls=CallyStackServiceCommand(),
    context_settings={'ignore_unknown_options': True},
)
@click.option(
    '--terraform-path',
    envvar='CALLY_TERRAFORM_PATH',
    type=click.Path(file_okay=True, dir_okay=False, executable=True),
    default='/usr/bin/terraform',
    help='Path to the terraform binary',
)
@click.option(
    '--terraform-cache',
    envvar='CALLY_TERRAFORM_CACHE',
    type=click.Path(path_type=Path),
    default=Path(Path.home().as_posix(), '.cache', 'cally'),
    help='Path to the services\' terraform plan/provider cache',
)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_obj
def run_terraform(
    config: CallyStackServiceConfig,
    terraform_path: str,
    terraform_cache: Path,
    args: Tuple[str, ...],
):
    terraform_cache.mkdir(exist_ok=True)
    with terraform.Command(
        service=config.config,
        terraform_path=terraform_path,
        terraform_cache=terraform_cache,
        arguments=args,
    ) as tf_cmd:
        with terraform.Action(service=config.config) as action:
            action.synth_stack()
            Path('cdk.tf.json').write_text(action.print(), encoding='utf-8')
        if not tf_cmd.success:
            click.secho(message=tf_cmd.stderr, fg='red')
            sys.exit(tf_cmd.returncode)
        click.secho(tf_cmd.stdout)


tf.add_command(print_template)
tf.add_command(run_terraform)
tf.add_command(write_template)
