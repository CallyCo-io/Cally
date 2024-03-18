import os
from unittest import mock

from cally.cli.config import CallyConfig

from ... import CallyTestHarness


class CallyConfigTests(CallyTestHarness):
    def test_service_name(self):
        config = CallyConfig(config_file='blah.yml')
        config.service = 'test'
        self.assertEqual(config.settings.name, 'test')

    def test_environment(self):
        config = CallyConfig(config_file='blah.yml')
        config.environment = 'test'
        self.assertEqual(config.settings.environment, 'test')

    @mock.patch.dict(os.environ, {"CALLY_SERVICE": "ignored"})
    def test_service_name_envvar_ignored(self):
        config = CallyConfig(config_file='blah.yml')
        config.service = 'test'
        self.assertEqual(config.settings.name, 'test')

    @mock.patch.dict(os.environ, {"CALLY_ENVIRONMENT": "ignored"})
    def test_environment_envvar_ignored(self):
        config = CallyConfig(config_file='blah.yml')
        config.environment = 'test'
        self.assertEqual(config.settings.environment, 'test')

    def test_defaults(self):
        config = CallyConfig(self.get_test_file('config/defaults.yaml'))
        data = {'PROVIDERS': {'test': {'foo': 'bar'}}}
        self.assertDictEqual(config.settings.to_dict(), data)

    def test_defaults_with_env(self):
        config = CallyConfig(self.get_test_file('config/defaults.yaml'))
        config.environment = 'harness'
        data = {'ENVIRONMENT': 'harness', 'PROVIDERS': {'test': {'foo': 'not-bar'}}}
        self.assertDictEqual(config.settings.to_dict(), data)

    def test_defaults_with_service(self):
        config = CallyConfig(self.get_test_file('config/defaults.yaml'))
        config.environment = 'harness'
        config.service = 'defaults'
        data = {
            'NAME': 'defaults',
            'ENVIRONMENT': 'harness',
            'PROVIDERS': {'test': {'foo': 'really-not-bar'}},
        }
        self.assertDictEqual(config.settings.to_dict(), data)

    @mock.patch.dict(os.environ, {"CALLY_PROVIDERS__TEST__FOO": "totally-not-bar"})
    def test_defaults_with_envvar_override(self):
        config = CallyConfig(self.get_test_file('config/defaults.yaml'))
        config.environment = 'harness'
        config.service = 'defaults'
        data = {
            'NAME': 'defaults',
            'ENVIRONMENT': 'harness',
            'PROVIDERS': {'test': {'foo': 'totally-not-bar'}},
        }
        self.assertDictEqual(config.settings.to_dict(), data)
