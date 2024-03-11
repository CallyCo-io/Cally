PROVIDER_PYPROJECT = """[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "CallyProviders$title"
version = "$version"
requires-python = ">=3.8"
authors = [
  {name = "Cally Generated"},
]
description = "Cally Generated $title Provider"

[tool.setuptools.packages.find]
include = ["cally.*"]

[tool.setuptools.package-data]
"*" = [
    "py.typed",
    "*.tgz",
]"""

PROVIDER_CDKTF = """{
  "language": "python",
  "app": "python3 ./main.py",
  "sendCrashReports": "false",
  "terraformProviders": [
    "$provider@~>$version"
  ],
  "terraformModules": [],
  "codeMakerOutput": "$path",
  "context": {}
}"""
