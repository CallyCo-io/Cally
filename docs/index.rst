.. rst-class:: hide-header

Welcome to Cally
================

Cally is a package intended to be the foundation for your Internal Developer
Platform.

It aims to be a robust, flexible, and opinionated starting point for your team
to get started building your own internal tooling. Without the need to learn all
the nuances of building a structured configuration based command line tool, and
with a focus on making the CDK for Terraform operate in a more pythonic manner.

Cally in three points:

-   flexible, layered, and opinonated configuration
-   extendible by design, with a strong focus on convention over configuration
-   built-in testing framework, to promote rapid iteration

Cally is not intended to be run directly, but rather included as a dependency
in your internal projects tooling. Cally takes advantage of Python's namespaces
to dynamically load in commands/resources/stacks/defaults from your project at
runtime.

.. code-block:: toml
    :caption: pyproject.toml

    [build-system]
    requires = ["setuptools"]
    build-backend = "setuptools.build_meta"

    [project]
    name = "minimal-idp"
    version = "0.1.0"
    dependencies = ["cally"]
    requires-python = ">=3.8"
    authors = [
      {name = "Example Org"},
    ]
    description = "Example Cally Extension"

    [tool.setuptools.packages.find]
    include=["cally.*"]

This is an example of minimal structure (reference from our `minimal example <https://github.com/CallyCo-io/cally-examples/tree/main/minimal>`_.)

.. code-block:: shell

    ├── cally
    │   └── idp
    │       ├── commands
    │       │   └── example.py
    │       ├── defaults.py
    │       └── stacks
    │           └── example.py
    ├── cally.yaml
    ├── pyproject.toml
    ├── README.md
    └── tests
        ├── __init__.py
        ├── testdata
        │   └── example.json
        └── test_minimal.py

Documentation
-------------

This part of the documentation guides you through all of the library's
usage patterns.

.. toctree::
   :maxdepth: 2

   concepts
   configuration
   cli

API Reference
-------------

This contains the information on a specific function, class, or
method.

.. toctree::
   :maxdepth: 2

   api

Miscellaneous Pages
-------------------

.. toctree::
   :maxdepth: 1

   license
