from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass
class CallyService:
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
        return self.stack_vars.get(var, default)

    def to_dict(self) -> dict:
        return asdict(self)
