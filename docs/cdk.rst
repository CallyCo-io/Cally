CDK
===
Continuing on from the generalised overview found in the :ref:`concepts`, Cally at
its core, was built to abstract and generate valid Terraform json, via the CDK for
Terraform.

-------------
CallyResource
-------------
This is used as a wrapper, to provide a convenient and pythonic interface to CDK
for Terraform resources. Though you can use constructs, I'd prefer to not work
around the nuances of very typescript feeling python, and just lean on the benfits
of the CDK for Terraform. Which is an extremely robust and reliable Terraform JSON
generator.

.. code-block:: python

    class RandomPet(CallyResource):
        provider = 'random'
        resource = 'random_pet'
        defaults = MappingProxyType({'prefix': 'foo')

This class when instantiated will generate a random pet name, prefixed by ``foo``.
defaults are copied via deepcopy, so complex structures can be defined here. If the
service provides a value, the default is ignored.


----------
CallyStack
----------
This is what will be instantiated during tf print/write commands, you have the freedom
to construct your stack, any way you see fit. Leaning on all the functionality availble
within python, without needing to be concerned about how to construct things in a 'CDK
for Terraform' way. Cally takes care of backend + provider configuration, leaving you to
focus entirely on service design.

A stack can be as minimal as adding a single resource, or as complex as building a full
service, including VMs, Load Balancers, Dashboards, secrets management, IAM, etc.

.. code-block:: python

    class PetRandom(CallyStack):
        def __init__(self, service: CallyStackService) -> None:
            super().__init__(service)
            self.add_resource(Pet('beagle'))

----------------
Example Use Case
----------------
This shows an example of building an IDP, that is able to generate Versioned Buckets
from very minimal configuration.

Project layout

.. code-block:: shell

    ├── cally
    │   └── idp
    │       ├── defaults.py
    │       ├── __init__.py
    │       ├── py.typed
    │       ├── resources
    │       │   ├── __init__.py
    │       │   └── storage.py
    │       └── stacks
    │           ├── gcp.py
    │           ├── __init__.py
    ├── cally.yaml
    └── pyproject.toml

defaults
--------
Defaults are where you set the things you'd like to be provided to all services, like
backend. Further details can be found in the :ref:`config-top-defaults` documentation.

.. code-block:: python
    :caption: defaults.py

    DEFAULTS = {
        'backend': {
            'config': {
                'bucket': 'my-state-files',
            },
            'path': '{environment}/{name}',
            'path_key': 'prefix',
            'type': 'GcsBackend',
        },
        'providers': {
            'google': {
                'region': 'australia-southeast1',
                'default_labels': {'deployment_tool': 'cally'},
            }
        },
    }

resources
---------
The intention is within your idp.resources, you'd build out a collection of the
resources your stacks will pull in. With any relevant defaults. For example, if
I were building out a storage stack, I would define all my resources and defaults
like this example:

.. note::
    It is expected that the class name match the CDK for Terraform class name,
    so that cally is able to resolve and instantiate the correct class when it
    is time to 'synth' the stack.

.. code-block:: python
    :caption: resources/storage.py

    from types import MappingProxyType


    class StorageBucket(CallyResource):
        provider = 'google'
        resource = 'storage_bucket'


    class StorageBucketLifecycleRule(CallyResource):
        provider = 'google'
        resource = 'storage_bucket'


    class StorageBucketLifecycleRuleCondition(CallyResource):
        provider = 'google'
        resource = 'storage_bucket'


    class StorageBucketLifecycleRuleAction(CallyResource):
        provider = 'google'
        resource = 'storage_bucket'


    class StorageBucketVersioning(CallyResource):
        provider = 'google'
        resource = 'storage_bucket'
        defaults = MappingProxyType({'enabled': True})

Whilst it is not strictly necessary to define attribute resources, you lose the
strict type checking you get by using them. So when a stack is synthed, you can
get an output that fails to be processed correctly by Terraform, due to things
like a string where an int is expected.


stacks
------

.. code-block:: python
    :caption: stacks/gcp.py

    from cally.cdk import CallyStack
    from cally.cli.config.config_types import CallyStackService
    from ..resources import storage


    class VersionedBucket(CallyStack):
        def __init__(self, service: CallyStackService) -> None:
            super().__init__(service)

            lifecycle_rule = storage.StorageBucketLifecycleRule(
                condition=storage.StorageBucketLifecycleRuleCondition(
                    days_since_noncurrent_time=service.get_stack_var('object_age', 30),
                    with_state='ARCHIVED',
                ),
                action=storage.StorageBucketLifecycleRuleAction(
                    type='Delete',
                ),
            )

            self.bucket = storage.StorageBucket(
                f'{self.name}-bucket',
                name=service.get_stack_var('bucket_name', self.name),
                location=service.get_stack_var('location', 'AUSTRALIA-SOUTHEAST1'),
                lifecycle_rule=[lifecycle_rule],
                versioning=storage.StorageBucketVersioning(),
            )
            self.add_resource(self.bucket)

cally.yaml
----------
Now that you have resources + a stack, you can create a config file that to generate
buckets with versioning automatically enabled.

.. code-block:: yaml
    :caption: cally.yaml

    defaults:
      providers:
        google:
          project: my-default-project

    dev:
      defaults:
        providers:
          google:
            project: my-dev-project
      services:
        versioned-defaults:
          stack_type: VersionedBucket
        versioned-customised:
          providers:
            google:
              project: another-buckety-project
              region: australia-southeast2
          backend:
            config:
              bucket: alternative-state-bucket
          stack_type: VersionedBucket
          stack_vars:
            bucket_name: my-bucket-name
            object_age: 7
            location: australia-southeast2

Results
-------
The resulting outputs from those service examples can be seen below

.. code-block:: json
    :caption: ➜  example git:(main) ✗ cally tf print --environment dev --service versioned-defaults

    {
      "//": {
        "metadata": {
          "backend": "gcs",
          "stackName": "versioned-defaults",
          "version": "0.20.5"
        },
        "outputs": {
        }
      },
      "provider": {
        "google": [
          {
            "default_labels": {
              "deployment_tool": "cally"
            },
            "project": "my-dev-project",
            "region": "australia-southeast1"
          }
        ]
      },
      "resource": {
        "google_storage_bucket": {
          "versioned-defaults-bucket": {
            "//": {
              "metadata": {
                "path": "versioned-defaults/versioned-defaults-bucket",
                "uniqueId": "versioned-defaults-bucket"
              }
            },
            "lifecycle_rule": [
              {
                "action": {
                  "type": "Delete"
                },
                "condition": {
                  "days_since_noncurrent_time": 30,
                  "with_state": "ARCHIVED"
                }
              }
            ],
            "location": "AUSTRALIA-SOUTHEAST1",
            "name": "versioned-defaults",
            "provider": "google",
            "versioning": {
              "enabled": true
            }
          }
        }
      },
      "terraform": {
        "backend": {
          "gcs": {
            "bucket": "my-state-files",
            "prefix": "dev/versioned-defaults"
          }
        },
        "required_providers": {
          "google": {
            "source": "hashicorp/google",
            "version": "5.23.0"
          }
        }
      }
    }

.. code-block:: json
    :caption: ➜  example git:(main) ✗ cally tf print --environment dev --service versioned-customised

    {
      "//": {
        "metadata": {
          "backend": "gcs",
          "stackName": "versioned-customised",
          "version": "0.20.5"
        },
        "outputs": {
        }
      },
      "provider": {
        "google": [
          {
            "default_labels": {
              "deployment_tool": "cally"
            },
            "project": "another-buckety-project",
            "region": "australia-southeast2"
          }
        ]
      },
      "resource": {
        "google_storage_bucket": {
          "versioned-customised-bucket": {
            "//": {
              "metadata": {
                "path": "versioned-customised/versioned-customised-bucket",
                "uniqueId": "versioned-customised-bucket"
              }
            },
            "lifecycle_rule": [
              {
                "action": {
                  "type": "Delete"
                },
                "condition": {
                  "days_since_noncurrent_time": 7,
                  "with_state": "ARCHIVED"
                }
              }
            ],
            "location": "australia-southeast2",
            "name": "my-bucket-name",
            "provider": "google",
            "versioning": {
              "enabled": true
            }
          }
        }
      },
      "terraform": {
        "backend": {
          "gcs": {
            "bucket": "alternative-state-bucket",
            "prefix": "dev/versioned-customised"
          }
        },
        "required_providers": {
          "google": {
            "source": "hashicorp/google",
            "version": "5.23.0"
          }
        }
      }
    }
