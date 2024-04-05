import inspect
from copy import deepcopy
from dataclasses import dataclass, field, make_dataclass
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
    _instantiated_attributes: dict = field(default_factory=dict)

    def instantiate_attributes(self) -> None:
        attrs = {}
        for key, val in self.__dict__.items():
            if key == '_instantiated_attributes':
                continue
            if hasattr(val, '_cdktf_resource'):
                attrs.update({key: val.construct_resource()})
                continue
            if isinstance(val, list):
                attrs.update(
                    {
                        key: [
                            (
                                x.construct_resource()
                                if hasattr(x, '_cdktf_resource')
                                else x
                            )
                            for x in val
                        ]
                    }
                )
                continue
            attrs.update({key: val})
        self._instantiated_attributes = attrs

    def to_dict(self) -> dict:
        if not self._instantiated_attributes:
            self.instantiate_attributes()
        return self._instantiated_attributes


class CallyResource:
    _cdktf_resource: Any  # This is probably a callable TerraformResource
    _identifier: Optional[str]
    _instantiated_resource: TerraformResource
    attributes: CallyResourceAttributes
    provider: str
    resource: str
    defaults: dict

    def __init__(self, identifier: Optional[str] = None, **kwargs) -> None:
        module = import_module(f'cally.providers.{self.provider}.{self.resource}')
        self._cdktf_resource = getattr(module, self.__class__.__name__)
        self.attributes = self._build_attributes(identifier, **kwargs)

    def __str__(self) -> str:
        if self.identifier:
            return f'${{{self.resource}.{self.identifier}.id}}'
        return self.__class__.__name__

    def __getattr__(self, item: str) -> Optional[str]:
        # TODO: This likely could use some improvement
        if item.startswith('__jsii'):
            return getattr(self._instantiated_resource, item)
        if item in {'attributes', 'defaults', '_instantiated_resource'}:
            return None
        if self.identifier:
            return f'${{{self.resource}.{self.identifier}.{item}}}'
        return None

    def _get_attribute_default(self, name: str) -> Any:
        if self.defaults is None:
            return None
        return deepcopy(self.defaults.get(name, None))

    def _build_attributes(
        self, identifier: Optional[str] = None, **kwargs
    ) -> CallyResourceAttributes:
        func = self._cdktf_resource.__init__  # type: ignore
        parameters = inspect.signature(func).parameters
        fields = [
            (name, param.annotation, self._get_attribute_default(name))
            for name, param in parameters.items()
            if param.annotation is not inspect._empty and name not in {'scope'}
        ]
        name = f'{self.__class__.__name__}CallyAttributes'
        cls = make_dataclass(name, fields, bases=(CallyResourceAttributes,))
        if identifier:
            # Some newer provider releases appear to use 'id_'
            id_field = 'id'
            if 'id_' in parameters:
                id_field = 'id_'
            kwargs.update({id_field: identifier})
        self._identifier = identifier
        return cls(**kwargs)

    @property
    def identifier(self) -> Optional[str]:
        return self._identifier

    def construct_resource(
        self,
        scope: Optional[Construct] = None,
        provider: Optional[TerraformProvider] = None,
    ) -> TerraformResource:
        if getattr(self, '_instantiated_resource', None) is None:
            attrubtes = self.attributes.to_dict()
            if scope and provider:
                attrubtes.update(
                    {
                        'scope': scope,
                        'provider': provider,
                    }
                )
            self._instantiated_resource = self._cdktf_resource(**attrubtes)
        return self._instantiated_resource


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
