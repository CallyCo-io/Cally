from dataclasses import asdict, dataclass, field, fields, is_dataclass
from typing import Any, Optional

from ..exceptions import ObjectNotDataclassError


def filter_dataclass_props(data: dict, cls: Any) -> dict:
    if not is_dataclass(cls):
        raise ObjectNotDataclassError(f'{cls} is not of type dataclass')
    return {x.name: data.get(x.name) for x in fields(cls) if x.name in data}


@dataclass
class CallyProject:
    pass


@dataclass
class CallyService(CallyProject):
    name: str
    environment: str


@dataclass
class CallyBackend:
    config: dict = field(default_factory=dict)
    type: str = 'LocalBackend'
    path: str = 'state/{environment}/{name}'
    path_key: str = 'path'

    def backend_config(self, service: dict) -> dict:
        return {self.path_key: self.path.format(**service), **self.config}


@dataclass
class CallyStackService(CallyService):
    """This dataclass is automatically passed to the CallyStack class during
    instantiation. Allowing access to any service property, though it is
    recommended to use the documented functions.
    """

    stack_type: str
    backend: CallyBackend = field(default_factory=CallyBackend)
    providers: dict = field(default_factory=dict)
    stack_vars: dict = field(default_factory=dict)

    def __setattr__(self, prop, val):
        if prop == 'backend' and isinstance(val, dict):
            super().__setattr__(prop, CallyBackend(**val))
            return
        super().__setattr__(prop, val)

    @property
    def backend_type(self) -> str:
        return self.backend.type

    @property
    def backend_config(self) -> dict:
        return self.backend.backend_config(self.to_dict())

    def get_provider_vars(self, provider: str) -> dict:
        return self.providers.get(provider, {})

    def get_stack_var(self, var: str, default: Optional[Any] = None) -> Any:
        """Any stack var, configured on the service is available via this method, with
        the ability to provide a default.
        """
        return self.stack_vars.get(var, default)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CallyEnvironment(CallyProject):
    environment: str
