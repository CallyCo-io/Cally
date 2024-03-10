import pkgutil
from importlib import import_module

from click import Group

package = import_module(__package__)
for _, name, is_pkg in pkgutil.walk_packages(package.__path__):  # noqa: B007
    full_name = f'{package.__name__}.{name}'
    module = import_module(full_name)
    for sub_module in dir(module):
        attr = getattr(module, sub_module)
        if isinstance(attr, Group):
            globals()[sub_module] = attr
