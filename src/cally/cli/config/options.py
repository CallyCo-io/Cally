from pathlib import Path
from typing import Union

import click


def ctx_callback(
    ctx: click.Context, param: click.Parameter, value: Union[str, int]
) -> Union[str, int]:
    setattr(ctx.obj, str(param.name), value)
    return value


CALLY_CONFIG_OPTIONS = [
    click.Option(
        ['--config-file'],
        type=click.Path(path_type=Path),
        default=Path(Path.cwd(), 'cally.yaml'),
        envvar='CALLY_CONFIG',
        help='Path to the project config file',
        expose_value=False,
        callback=ctx_callback,
    )
]

CALLY_ENVIRONMENT_OPTIONS = [
    *CALLY_CONFIG_OPTIONS,
    click.Option(
        ['--environment'],
        envvar='CALLY_ENVIRONMENT',
        expose_value=False,
        required=True,
        help='Environment to operate within',
        callback=ctx_callback,
    ),
]

CALLY_SERVICE_OPTIONS = [
    *CALLY_ENVIRONMENT_OPTIONS,
    click.Option(
        ['--service'],
        envvar='CALLY_SERVICE',
        expose_value=False,
        required=True,
        help='Service name to retrieve config details',
        callback=ctx_callback,
    ),
]
