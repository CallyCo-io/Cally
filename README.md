# Cally
A config as infrastructure foundation for your Internal Developer Platform

### Why
To provide a powerful, but consisent configuration, and CLI to common Platform Engineering tasks

### Features
- Multi layered configuration provided by Dyanconf
- Built-in testing harness
- Unit testing for your IaC
- Abstraction of the CDK for Terraform
- Build Terraform JSON, for consumption by [OpenTofu](https://opentofu.org/) or [Terraform](https://www.terraform.io/)

## Concepts
Cally isn't intended to be consumed directly, but rather as a dependency of your internal IDP tool.

### Python Packaging
To give a consistent experience across your Developers/Engineers/CI/CD, packaging your tooling, and providers, should be vailable via your internal python registry.

Internal Registry options
- [Self Hosted](https://packaging.python.org/en/latest/guides/hosting-your-own-index/)
- [Google Artifact Registry](https://cloud.google.com/artifact-registry)
- [AWS CodeArtifact](https://docs.aws.amazon.com/codeartifact/latest/ug/using-python.html)

This `pyproject.toml` example from our [minimal example](https://github.com/CallyCo-io/cally-examples/tree/main/minimal), is enough to produce an empty stack, or run our hello world exampe command.
```toml
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

[project.scripts]
minimal-idp = "cally.cli:cally"

[project.optional-dependencies]
test = [
  "black",
  "build",
  "mypy",
  "pytest",
  "pytest-black",
  "pytest-mypy",
  "pytest-ruff<0.3",  # 0.3 + 0.3.1 are currently not working
  "ruff",
]

[tool.black]
skip-string-normalization = true

[tool.pytest.ini_options]
testpaths = "tests"
addopts = "-p no:cacheprovider --black --mypy --ruff"
filterwarnings = [
    "ignore",
    "default:::cally.*",
    "default:::tests.*"
]

[tool.ruff]
preview = true

[tool.ruff.lint]
select = [
    # flake8
    "A", "ARG", "B", "BLE", "C4", "PIE", "RET", "SIM", "S",
    "F",  # pyflakes
    "N",  # pep8-nameing
    "PL", # pylint
    "E",  # error
    "W",  # warning
    "PTH", # pathlib
    "RUF", # ruff
]
```
### Project Structure
Cally relies heavily on Python namespacing, and expects a structure following this convention:

```
├── cally
│   └── idp
│       ├── commands
│       │   ├── example.py
│       │   └── __init__.py
│       ├── defaults.py
│       ├── __init__.py
│       ├── py.typed
│       ├── resources
│       │   ├── __init__.py
│       │   └── random.py
│       └── stacks
│           ├── __init__.py
│           └── pets.py
├── cally.yaml
├── pyproject.toml
├── README.md
└── tests
    ├── __init__.py
    ├── test_cli.py
    ├── testdata
    │   └── random-pets.json
    └── test_stacks.py
```

## Configuration
Cally is built on top of Dynaconf, with an opinionated loader. This can of course be [overriden](https://www.dynaconf.com/advanced/#creating-new-loaders), however the default is intended to provide a robust, but flexible interface. By default it will load a `cally.yaml` in your current working directory, but is only necessary if you wish to pass configuration to your services.

### Service
When configuring a service, you can pass in the service name via `--service name` or via the environment variable `CALLY_SERVICE`

### Environment
When configuring a service, you can pass in the service name via `--environment name` or via the environment variable `CALLY_ENVIRONMENT`

### Example `cally.yaml`
This is the expected layout of a `cally.yaml`. The layers have a resolution order, from left to right, with the last winning. Objects are combined as per Dynaconf's [merging](https://www.dynaconf.com/merging/) strategy.

```yaml
defaults:
    provider:
        random:
            alias: foo
development:
    provider:
        random:
            alias: bar
    services:
        test-service:
            provider:
                random:
                    alias: this-wins
            stack_type: CallyStack
            stack_vars:
                example: variable
```
The output of test service would look like
```bash
$ cally config print-service --environment development --service test-service
ENVIRONMENT: development
NAME: test-service
PROVIDER:
  random:
    alias: this-wins
STACK_TYPE: CallyStack
STACK_VARS:
  example: variabl
```
As a contrived example, this is what a tf print would output
```json
{
  "//": {
    "metadata": {
      "backend": "local",
      "stackName": "test-service",
      "version": "0.20.5"
    },
    "outputs": {
    }
  },
  "terraform": {
    "backend": {
      "local": {
        "path": "state/development/test-service"
      }
    }
  }
}
```

### Defaults
The cally loader will attempt to load your projects defaults, from the `DEFAULTS` key, from the defaults namespace in your project.

From the earlier example project layout, a `defaults.py` with the following contents
```python
DEFAULTS = {
    "providers": {
        'random': {
            'alias': 'minimal'
        }
    }
}
```
Would result in the random provider being configured with an alias default of `minimal`

## Notes
This project is still in its early stages, documentation will be the next focal point, along with any bugs/oversights not found during early development.
