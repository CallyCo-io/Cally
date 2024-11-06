import inspect
from copy import deepcopy
from dataclasses import dataclass, field, make_dataclass
from importlib import import_module
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from cdktf import (
    App,
    TerraformBackend,
    TerraformOutput,
    TerraformProvider,
    TerraformResource,
    TerraformStack,
)
from constructs import Construct

if TYPE_CHECKING:
    from cally.cli.config.config_types import CallyStackService


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
    """This resource is for referencing the underlying CDK for Terraform resource,
    so that it can be later instantiated. This allows us to maniuplate variables on
    ``__init__``, along with setting defaults. Top level resources *must* be wrapped in
    this class, and attributes with a class specification *may* be wrapped with this
    for the purposes of setting defaults. Otherwise as long as the object structure
    is valid for the resource, the CDK will do the RightThings :TM:, however they will
    *not* be type checked and an output may succeed, but fail to validate/plan/apply.

    :param tf_identifier: This is required for the top level resource class, and
                          invalid for resource attributes. It is recommended to
                          specify this as the first argument rather than as a keyword.
                          This is expected to be a string, for consistency it should
                          follow the Identifier requirements set out by Terraform, but
                          the CDKTF will attempt to normalise it.

    """

    _cdktf_resource: Any  # This is probably a callable TerraformResource
    _tf_identifier: Optional[str]
    _instantiated_resource: TerraformResource
    attributes: CallyResourceAttributes

    #: Provider name, this is so cally knows where to load the underlying cdktf resource
    #: from. For example ``random``.
    provider: str
    #: Resource name, that cally will load the matching class name from, for example
    #: RandomPet, lives in ``random_pet``.
    resource: str
    #: A dictionary of the default values to set on instantion, if not passed through
    #: as kwargs. Wrapping in a MappingProxyType avoids the mutable warnings. For
    #: example ``MappingProxyType({'prefix': 'foo'})``
    defaults: Union[dict, MappingProxyType]

    def __init__(self, tf_identifier: Optional[str] = None, **kwargs) -> None:
        module = import_module(f'cally.providers.{self.provider}.{self.resource}')
        self._cdktf_resource = getattr(module, self.__class__.__name__)
        self.attributes = self._build_attributes(tf_identifier, **kwargs)

    def __str__(self) -> str:
        if self.tf_identifier:
            return f'${{{self.tf_resource}.{self.tf_identifier}.id}}'
        return self.__class__.__name__

    def __getattr__(self, item: str) -> Optional[str]:
        # TODO: This likely could use some improvement
        if item.startswith('__jsii'):
            return getattr(self._instantiated_resource, item)
        if item in {'attributes', 'defaults', '_instantiated_resource'}:
            return None
        if self.tf_identifier:
            return f'${{{self.tf_resource}.{self.tf_identifier}.{item}}}'
        return None

    def _get_attribute_default(self, name: str) -> Any:
        if self.defaults is None:
            return None
        return deepcopy(self.defaults.get(name, None))

    def _build_attributes(
        self, tf_identifier: Optional[str] = None, **kwargs
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
        if tf_identifier:
            # Some newer provider releases appear to use 'id_'
            id_field = 'id'
            if 'id_' in parameters:
                id_field = 'id_'
            kwargs.update({id_field: tf_identifier})
        self._tf_identifier = tf_identifier
        return cls(**kwargs)

    @property
    def tf_identifier(self) -> Optional[str]:
        return self._tf_identifier

    @property
    def tf_resource(self) -> Optional[str]:
        if self.resource.startswith('data_'):
            return f'data.{self.resource[5:]}'
        return self.resource

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
    """This forms the parent of your custom stacks. It has a number of convenience
    methods, and it is intended that you override ``__init__``, call super, and
    construct your own stack from there.
    """

    _outputs: List[Tuple[str, str]]
    _providers: Dict[str, TerraformProvider]
    _resources: List[CallyResource]
    service: 'CallyStackService'

    def __init__(self, service: 'CallyStackService') -> None:
        self.service = service

    def add_output(self, tf_identifier: str, output: str) -> None:
        """Adds a terraform output to the resulting generated terraform."""
        self.outputs.append((tf_identifier, output))

    def add_resource(self, resource: CallyResource) -> None:
        """Adds a CallyResource to the stack, all resources must be added to the
        stack from them to be including in the resutling output
        """
        self.resources.append(resource)

    def add_resources(self, resources: List[CallyResource]) -> None:
        """Adds a list of CallyResources to the stack"""
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
    def outputs(self) -> List[Tuple[str, str]]:
        if getattr(self, '_outputs', None) is None:
            self._outputs = []
        return self._outputs

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
                for tf_identifier, value in stack.outputs:
                    TerraformOutput(self, tf_identifier, value=value)
                stack.get_backend()(self, **stack.service.backend_config)

        app = App(outdir=outdir)
        MyStack(app)

        app.synth()
