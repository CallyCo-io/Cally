from contextlib import suppress
from importlib import import_module
from inspect import isclass
from pkgutil import walk_packages

from .. import CallyStack


def gather_stacks(package_name: str) -> None:
    package = import_module(package_name)
    for _, name, is_pkg in walk_packages(package.__path__):  # noqa: B007
        module = import_module(f'{package.__name__}.{name}')
        for sub_module in dir(module):
            if sub_module == 'CallyStack':
                continue
            attr = getattr(module, sub_module)
            if not isclass(attr):
                continue
            if issubclass(attr, CallyStack):
                globals()[sub_module] = attr


gather_stacks(__package__)
with suppress(ModuleNotFoundError):
    gather_stacks('cally.idp.stacks')
