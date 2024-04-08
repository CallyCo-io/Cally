.. _configuration:

=============
Configuration
=============
Cally's configuration is built on top of `dynaconf <https://www.dynaconf.com/>`_ with a custom loader to
provide a layered, consitent builder to provide a strong starting point for building your infrastructure
from a very small amount of configuration.

Cally firmly leans hard on the layered with merged config approach available within Dynaconf. With the
following resolution order, last set, wins: :ref:`config-idp-defaults`, :ref:`config-top-defaults`,
:ref:`config-environment`, :ref:`mixins`, and finally the Service itself. Dynaconf's `merging <https://www.dynaconf.com/merging/>`_
is enabled by default, and has the same `caveats <https://www.dynaconf.com/merging/#known-caveats>`_.

At first glance, this may seem quite complex, the layered approach allows for a powerful 'DRY' approach
without a lot of cognitive load.

cally.yaml
==========
Whislt cally is a tool that is built around configuration, it leans into convention over configuration to
reduce the amount of effort required to get started, improve consistency, and constraining the scope for
bugs, or mis-understood configuration.

---------
Top Level
---------
In this section we'll go into the various top level configuration keys.

.. _config-top-defaults:

defaults
--------
Any second level key configured here will be availble to all services, in all enviroments.

.. code-block:: yaml
    :caption: cally.yaml

    defaults:
      providers:
        random:
          alias: foo

.. _mixins:

mixins
------
Any key can be defined as a set of resuable components. For exampple if you had a common set of envrionment variables to
be available to multiple services, but not all services in an enviroment or project.

The following rules apply

- Mixins are set via the ``mixins`` key on a service, and is expected to be a yaml list
- They are processed in order of first to last
- Mixins can be in both the top level, and environment level. If they share a name, the global will be loaded, followed by the environment
- They will be merged following Dynaconf's merging strategy, and has the same caveats


.. code-block:: yaml
    :caption: cally.yaml

    mixins:
      example-mixin:
        providers:
          random:
            alias: foo
        stack_vars:
          list_var:
            - one
          dict_var:
            foo: bar
    dev:
      mixins:
        another:
          stack_type: ExampleStack
          stack_vars:
            list_var:
              - two
            dict_var:
              foo: foo
              bar: foo
      services:
        example-service:
          mixins:
            - example-mixin
            - another

.. code-block:: shell

    ✗ cally config print-service --environment dev --service example-service
    ENVIRONMENT: dev
    NAME: example-service
    PROVIDERS:
      random:
        alias: foo
    STACK_TYPE: ExampleStack
    STACK_VARS:
      dict_var:
        bar: foo
        foo: foo
      list_var:
      - one
      - two

.. _config-environment:

environment
-----------
Any top level key, that does not match `mixins` or `defaults`, will be considered to be an environment that
can be called using the ``--environment`` option or set via the ``CALLY_ENVIRONEMNT`` environment variable.

Mixins, and defaults can be set at an environment level, and all services are expected to be defined using
the ``services`` key.

.. code-block:: yaml
    :caption: cally.yaml

    dev:
      defaults:
        providers:
          random:
            alias: bar
      mixins:
        example-mixin:
          stack_var:
            my_key: value
      services:
        example-service:
          mixins:
            - example-mixin
          stack_type: ExampleStack

.. code-block:: shell

    ✗ cally config print-service --environment dev --service example-service
    ENVIRONMENT: dev
    NAME: example-service
    PROVIDERS:
      random:
        alias: bar
    STACK_TYPE: ExampleStack
    STACK_VAR:
      my_key: value

------------
Second Level
------------
All keys in the second level, can be set in **all** levels. From the defaults, to the environment defaults,
mixins, and the service level.

backend
-------
Terraform requires a backend to store state files. By default this will be a ``LocalBackend``, but it is
quite useful to set your in your idp defaults. The backend key has the following keys

- ``type`` - this sets the backend to be used ie ``LocalBackend``
- ``path`` - will be formatted using pythons builtin `str.format <https://docs.python.org/3/library/stdtypes.html#str.format>`_, and all keys in the ``service`` object are avaialble using the `format syntax <https://docs.python.org/3/library/string.html#formatstrings>`_.
- ``path_key`` - The prefix to the state file varies per backend. For example, ``LocalBackend`` uses ``path``, and ``GcsBackend`` uses ``prefix``
- ``config`` - A dictionary for the configuration to be suplied to the provider

.. code-block:: yaml
    :caption: cally.yaml

    defaults:
      backend:
        config:
          bucket: my-orgs-state-bucket
        path: my/path/to/{environment}/{name}
        path_key: prefix
        type: GcsBackend

.. code-block:: json
    :caption: cdk.tf.json

    {
      "terraform": {
        "backend": {
          "gcs": {
            "bucket": "my-orgs-state-bucket",
            "prefix": "my/path/to/dev/example-service"
          }
        }
      }
    }

providers
---------
The providers key, is where provider configuration defaults will live. Useful for setting things like
a default region. These will be passed to the provider automatically during instantiation.

.. code-block:: yaml
    :caption: cally.yaml

    dev:
      defaults:
        providers:
          google:
        default_labels:
          deployment_tool: cally
          git_repo: cally-examples
        project: cally-project
        region: australia-southeast1

.. code-block:: shell

    ✗ cally config print-service --environment dev --service example-service
    ENVIRONMENT: dev
    NAME: example-service
    PROVIDERS:
      google:
        default_labels:
          deployment_tool: cally
          git_repo: cally-examples
        project: cally-project
        region: australia-southeast1

stack_type
----------
``stack_type`` is specific to Terraform commands, this will inform cally to load a stack from the
available :ref:`concepts-stacks` and instanitate it with a ``CallyStackService`` object at run time.

.. code-block:: yaml
    :caption: cally.yaml

    dev:
      services:
        example:
          stack_type: ExampleStack

.. code-block:: shell

    ✗ cally tf print --environment dev --service example
    {
      "//": {
        "metadata": {
          "backend": "local",
          "stackName": "example",
          "version": "0.20.6"
        },
        "outputs": {
        }
      },
      "terraform": {
        "backend": {
          "local": {
            "path": "example/dev"
          }
        }
      }
    }


stack_vars
----------
``stack_vars`` are available to the stack via `self.service.get_stack_var('key', [default])`, and contain any valid
yaml structure.

.. code-block:: yaml
    :caption: cally.yaml

    dev:
      services:
        example:
          stack_type: ExampleStack
          stack_vars:
            foo: bar


.. code-block:: python

    class ExampleStack(CallyStack):

    def __init__(self, service: CallyStackService) -> None:
        super().__init__(service)
        self.add_output('foo', self.service.get_stack_var('foo', 'foo'))
        self.add_output('bar', self.service.get_stack_var('bar', 'foo'))

.. code-block:: shell

    ✗ cally tf print --environment dev --service example
    {
      "//": {
        "metadata": {
          "backend": "local",
          "stackName": "example",
          "version": "0.20.6"
        },
        "outputs": {
          "example": {
            "bar": "bar",
            "foo": "foo"
          }
        }
      },
      "output": {
        "bar": {
          "value": "foo"
        },
        "foo": {
          "value": "bar"
        }
      },
      "terraform": {
        "backend": {
          "local": {
            "path": "example/dev"
          }
        }
      }
    }

.. _config-idp-defaults:

IDP Defaults
============
Often there will be certain constants, that would make sensible defaults, say provider defaults
for ``region``, or your state bucket and path name. These can be configured via a ``DEFAULTS`` key
within your ``cally.idp.defaults`` file.

.. code-block:: python
   :caption: defaults.py

    DEFAULTS = {
        'providers': { 'google': { 'location': 'some-place1' }},
        'backend': {
            'type': 'GcsBackend', 'path_key': 'prefix',
            'path': 'state-files/{environment}/{name}',
            'config': { 'bucket': 'buckety-mc-bucketface' },
        },
    }

Which will be available to the consuming services as required

.. code-block:: shell

    ✗ cally config print-service --environment dev --service pets
    BACKEND:
      config:
        bucket: buckety-mc-bucketface
      path: state-files/{environment}/{name}
      path_key: prefix
      type: GcsBackend
    ENVIRONMENT: dev
    NAME: pets
    PROVIDERS:
      google:
        location: some-place1
    STACK_TYPE: RandomPets


Overriding Cally's Loader
=========================
Dynaconf does allow for the loaders to be overriden, there may be further support added to this directly,
however for now, you can at least append your own loader via the `documented methods <https://www.dynaconf.com/advanced/#creating-new-loaders>`_.

For example, creating a ``loader.py`` in the ``cally.idp`` namespace, you could set an environment variable like
``export LOADERS_FOR_DYNACONF="['cally.idp.loader']"``. With the following contents

.. code-block:: python

    from dynaconf import LazySettings


    def cat_all_values(settings: LazySettings) -> None:
        for k, v in settings.items():
            if isinstance(v, dict):
                cat_all_values(v)
            else:
                settings[k] = 'meow'


    def load(obj: LazySettings, *args, **kwargs) -> None:  # noqa: ARG001
        cat_all_values(obj)

Whilst the results are meow amusing, I'm sure a more useful use case could be found for this
functionality.

.. code-block:: shell

    ✗ cally config print-service --environment test --service test
    BACKEND:
      config:
        bucket: meow
      path: meow
      path_key: meow
      type: meow
    BACKEND.PATH: meow
    BACKEND.TYPE: meow
    ENVIRONMENT: meow
    NAME: meow
    PROVIDERS:
      google:
        default_labels:
          deployment_tool: meow
          git_repo: meow
        project: meow
        region: meow
