import inspect
from copy import deepcopy
from dataclasses import dataclass, make_dataclass
from importlib import import_module
from typing import TYPE_CHECKING, Any, List

from cdktf import (
    App,
    LocalBackend,
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
        return f'${{{self.resource}.{self.attributes.id}.id}}'

    def __getattr__(self, item: str) -> str:
        if item.startswith('__jsii'):
            return getattr(self._instantiated_resource, item)
        return f'${{{self.resource}.{self.attributes.id}.{item}}}'

    def _get_attribute_default(self, name: str) -> Any:
        if not hasattr(self, 'defaults'):
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
        return cls(**{'id_': identifier, **kwargs})

    def construct_resource(self, scope: Construct, provider: TerraformProvider) -> None:
        self.attributes.provider = provider
        self._instantiated_resource = self._cdktf_resource(
            scope, **self.attributes.__dict__
        )


class CallyStack:
    _resources: List[CallyResource]
    service: 'CallyStackService'

    def __init__(self, service: 'CallyStackService') -> None:
        self.service = service

    def add_resource(self, resource: CallyResource) -> None:
        self.resources.append(resource)

    def add_resources(self, resources: List[CallyResource]) -> None:
        self.resources.extend(resources)

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

    def synth_stack(self, outdir='cdktf.out'):
        stack = self

        class MyStack(TerraformStack):

            def __init__(self, scope: Construct) -> None:
                super().__init__(scope, stack.name)
                # TODO: Build provider loader
                for resource in stack.resources:
                    provider = TerraformProvider(self, 'test')  # type: ignore
                    resource.construct_resource(self, provider=provider)

                LocalBackend(
                    self, path=f'state/{stack.name}.tfstate'
                )  # TODO: load this

        app = App(outdir=outdir)
        MyStack(app)

        app.synth()
