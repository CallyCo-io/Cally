from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CallyService:
    name: str
    environment: str


@dataclass
class CallyStackService(CallyService):
    stack_type: str
    providers: dict = field(default_factory=dict)
    stack_vars: dict = field(default_factory=dict)

    def get_provider_vars(self, provider: str) -> dict:
        return self.providers.get(provider, {})

    def get_stack_var(self, var: str, default: Optional[Any] = None) -> Any:
        return self.stack_vars.get(var, default)
