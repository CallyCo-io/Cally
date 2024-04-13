.. _concepts:

========
Concepts
========
There are concepts and assumptions made about the intended use case for
Cally, this page will attempt to cover them.

Python Namespaces
=================
Cally relies heavily on Python `namespace packages <https://packaging.python.org/en/latest/guides/packaging-namespace-packages/>`_

The tool comes with the following namespaces built in:

- `cally.cli` - Command line, and configuration tools
- `cally.cdk` - A collection of utilities for building CDK for Terraform stacks
- `cally.testing` - Base testing harnesses for testing the command line + stacks

A big focus for Cally is the generation of Terraform templates via the
CDK for Terraform. All providers built by Cally, and installed will be availble
under the following namespace:

- `cally.providers`

When building your IDP tool on top of Cally, it's expected that your code reside
in the following namespace:

- `cally.idp`

Further detail for each of the following sub namespaces will be covered in this
document, but they are listed here

- `cally.idp.commands` - All your internal commands
- `cally.idp.resources` - Where you configure the defaults of each of your terraform resources
- `cally.idp.stacks` - This is where you will build your Terraform 'Stacks'
- `cally.idp.defaults` - Where the defaults for your tool exist, ie default region for your google provider

CLI
===
Cally's commmand line interface is built on the shoulders of `click <https://click.palletsprojects.com/>`_, which
is an incredibly powerful library, and has provided the foundation of the tool.

Commands
--------
Any command group added to your `cally.idp.commands`, namespace will be available as a cally subcommand. For
example:

.. code-block:: python

    import click

    @click.group()
    def example() -> None:
        pass

    @click.command()
    @click.argument('name')
    def hello(name: str):
        click.secho(f'Hello {name}')

    example.add_command(hello)

Would be availble as:

.. code-block:: shell

    ✗ cally example hello world
    Hello world

Configuration
=============
Cally's configuration is built on top of `dynaconf <https://www.dynaconf.com/>`_ with a custom loader to
provide a layered, consitent builder to provide a strong starting point for building your infrastructure
from a very small amount of configuration. Further details can be found in the :ref:`configuration` section.

cally.yaml
----------
Cally will look for a `cally.yaml` in your working directory and load it. The expected layout is as
follows:

.. code-block:: yaml

    defaults:
    # All defaults here
    development:
        services:
            test-service:
                stack_type: CallyStack
                stack_vars:
                    example: variable


The CDK for Terraform
=====================
One of the nuances of the CDK for Terraform, is that (IMHO) very boilerplate heavy, and feels
a lot like writing `typescript <https://github.com/aws/jsii>`_ or HCL, that happens to look like
python. Though you can use constructs and other functions, being able to focus purely on the
building blocks for your infrastructure and tooling, while allowing the CDK for Terraform to
produce extremely consistent and strongly typed templates.

.. note::
    As jsii is integral to the CDK for Terraform, `Node.js <https://nodejs.org/en>`_ must be
    available in your path.

Resources
---------
Cally provides a wrapper for the resources, this is a good place to set defaults. Which can be
of Any type, including resource attributes, dicts, etc. On instation, these defaults will be
copied using `deepcopy`, avoiding issue related to memory refs being shared across child classes.

- `provider` - This is the namespace of the resource built by the provider builder.
- `resource` - All cdk providers built after 0.7.0, have a coresponding module that
               matches the resource listed in the documentation/HCL spec.
- `defaults` - This is a dictionary, where you can define the defaults for that resource type.

Example:

.. code-block:: python

    class Pet(CallyResource):
        provider = 'random'
        resource = 'pet'
        defaults = {
            'length': 3,
            'separator': ' ',
        }

When consumed in a stack, would have an output like this:

.. code-block:: json

    {
      "random_pet": {
        "random-pet": {
          "//": {
            "metadata": {
              "path": "pets/random-pet",
              "uniqueId": "random-pet"
            }
          },
          "length": 3,
          "provider": "random.foo",
          "separator": " "
        }
      }
    }

.. _concepts-stacks:

Stacks
------
The goal of a `CallyStack` is to abstract away all of the boiler plate of setting up CDK for
Terraform stack. Along with taking care of configuring the providers as per the service and
defaults defined, it also configures the backend. You are free to construct this class, using
all the python tools at your disposal. All resources that are added using the `add_resource(resource)`
or `add_resources([resource, another])` commands, will be included in the resulting Terraform JSON.

.. code-block:: python

    class RandomPets(CallyStack):

    def __init__(self, service: CallyStackService) -> None:
        super().__init__(service)
        random_pet = Pet('random-pet')
        self.add_resource(random_pet)

When print called, this would be the output

.. code-block:: json

    {
      "//": {
        "metadata": {
          "backend": "local",
          "stackName": "pets",
          "version": "0.20.5"
        },
        "outputs": {
        }
      },
      "provider": {
        "random": [
          {
            "alias": "foo"
          }
        ]
      },
      "resource": {
        "random_pet": {
          "random-pet": {
            "//": {
              "metadata": {
                "path": "pets/random-pet",
                "uniqueId": "random-pet"
              }
            },
            "length": 3,
            "provider": "random.foo",
            "separator": " "
          }
        }
      },
      "terraform": {
        "backend": {
          "local": {
            "path": "state/dev/pets"
          }
        },
        "required_providers": {
          "random": {
            "source": "hashicorp/random",
            "version": "3.6.0"
          }
        }
      }
    }
