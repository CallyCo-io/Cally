import inspect
from copy import deepcopy
from dataclasses import dataclass, make_dataclass
from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from cdktf import (
    App,
    TerraformBackend,
    TerraformProvider,
    TerraformResource,
    TerraformStack,
)
from constructs import Construct

if TYPE_CHECKING:
    from cally.cli.config.types import CallyStackService


@dataclass
class CallyResourceAttributes:
    id: str
    provider: TerraformProvider


class CallyResource:
    _cdktf_resource: Any  # This is probably a callable TerraformResource
    _id_field: str
    _instantiated_resource: TerraformResource
    attributes: CallyResourceAttributes
    provider: str
    resource: str
    defaults: dict

    def __init__(self, identifier: str, **kwargs) -> None:
        module = import_module(f'cally.providers.{self.provider}.{self.resource}')
        self._cdktf_resource = getattr(module, self.__class__.__name__)
        self.attributes = self._build_attributes(identifier, **kwargs)

    def __str__(self) -> str:
        return f'${{{self.resource}.{self.identifier}.id}}'

    def __getattr__(self, item: str) -> Optional[str]:
        # TODO: This likely could use some improvement
        if item.startswith('__jsii'):
            return getattr(self._instantiated_resource, item)
        if item in {'attributes', 'defaults'}:
            return None
        return f'${{{self.resource}.{self.identifier}.{item}}}'

    def _get_attribute_default(self, name: str) -> Any:
        if self.defaults is None:
            return None
        return deepcopy(self.defaults.get(name, None))

    def _build_attributes(self, identifier: str, **kwargs) -> CallyResourceAttributes:
        func = self._cdktf_resource.__init__  # type: ignore
        parameters = inspect.signature(func).parameters
        fields = [
            (name, param.annotation, self._get_attribute_default(name))
            for name, param in parameters.items()
            if param.annotation is not inspect._empty and name not in {'scope'}
        ]
        name = f'{self.__class__.__name__}CallyAttributes'
        cls = make_dataclass(name, fields, bases=(CallyResourceAttributes,))
        # Some newer provider releases appear to use 'id_'
        self._id_field = 'id'
        if 'id_' in parameters:
            self._id_field = 'id_'
        return cls(**{self._id_field: identifier, **kwargs})

    @property
    def identifier(self) -> str:
        return getattr(self.attributes, self._id_field)

    def construct_resource(self, scope: Construct, provider: TerraformProvider) -> None:
        self.attributes.provider = provider
        self._instantiated_resource = self._cdktf_resource(
            scope, **self.attributes.__dict__
        )


class CallyStack:
    _providers: Dict[str, TerraformProvider]
    _resources: List[CallyResource]
    service: 'CallyStackService'

    def __init__(self, service: 'CallyStackService') -> None:
        self.service = service

    def add_resource(self, resource: CallyResource) -> None:
        self.resources.append(resource)

    def add_resources(self, resources: List[CallyResource]) -> None:
        self.resources.extend(resources)

    def get_backend(self) -> TerraformBackend:
        mod = import_module('cdktf')
        return getattr(mod, self.service.backend_type)

    def get_provider(self, scope: Construct, provider: str) -> TerraformProvider:
        if provider not in self.providers:
            # google_beta -> GoogleBetaProvider
            resource = f"{provider.capitalize().replace('_', '')}Provider"
            module = import_module(f'cally.providers.{provider}.provider')
            cls = getattr(module, resource)
            self.providers.update(
                {
                    provider: cls(
                        scope, id=provider, **self.service.providers.get(provider, {})
                    )
                }
            )
        prov = self.providers.get(provider)
        if prov is None:
            raise ValueError("Provider instantion failed")
        return prov

    @property
    def name(self) -> str:
        return self.service.name

    @property
    def environment(self) -> str:
        return self.service.environment

    @property
    def resources(self) -> List[CallyResource]:
        if getattr(self, '_resources', None) is None:
            self._resources = []
        return self._resources

    @property
    def providers(self) -> Dict[str, TerraformProvider]:
        if getattr(self, '_providers', None) is None:
            self._providers = {}
        return self._providers

    def synth_stack(self, outdir='cdktf.out'):
        stack = self

        class MyStack(TerraformStack):

            def __init__(self, scope: Construct) -> None:
                super().__init__(scope, stack.name)
                for resource in stack.resources:
                    resource.construct_resource(
                        self,
                        provider=stack.get_provider(self, resource.provider),
                    )
                stack.get_backend()(self, **stack.service.backend_config)

        app = App(outdir=outdir)
        MyStack(app)

        app.synth()
