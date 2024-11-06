import os
from pathlib import Path
from unittest import mock

from dynaconf import ValidationError

from cally.cli.config import config_types
from cally.cli.config.environment import CallyEnvironmentConfig
from cally.cli.config.service import CallyServiceConfig
from cally.cli.config.terraform_service import CallyStackServiceConfig

from ... import CallyTestHarness


class CallyServiceConfigTests(CallyTestHarness):
    def test_service_name(self):
        config = CallyServiceConfig()
        config.config_file = Path('blah.yaml')
        config.service = 'test'
        self.assertEqual(config.settings.name, 'test')

    def test_empty_service(self):
        config = CallyServiceConfig()
        config.config_file = Path('blah.yaml')
        config.environment = 'empty'
        config.service = 'empty'
        data = {'ENVIRONMENT': 'empty', 'NAME': 'empty'}
        self.assertDictEqual(config.settings.to_dict(), data)

    def test_environment(self):
        config = CallyServiceConfig()
        config.config_file = Path('blah.yaml')
        config.service = 'test'
        config.environment = 'test'
        self.assertEqual(config.settings.environment, 'test')

    @mock.patch.dict(os.environ, {"CALLY_SERVICE": "ignored"})
    def test_service_name_envvar_ignored(self):
        config = CallyServiceConfig()
        config.config_file = 'blah.yaml'
        config.service = 'test'
        self.assertEqual(config.settings.name, 'test')

    @mock.patch.dict(os.environ, {"CALLY_ENVIRONMENT": "ignored"})
    def test_environment_envvar_ignored(self):
        config = CallyServiceConfig()
        config.config_file = Path('blah.yaml')
        config.service = 'test'
        config.environment = 'test'
        self.assertEqual(config.settings.environment, 'test')

    def test_defaults(self):
        config = CallyServiceConfig()
        config.config_file = self.get_test_file('config/defaults.yaml')
        config.service = 'test'
        data = {'NAME': 'test', 'PROVIDERS': {'test': {'foo': 'bar'}}}
        self.assertDictEqual(config.settings.to_dict(), data)

    def test_defaults_with_env(self):
        config = CallyServiceConfig()
        config.config_file = self.get_test_file('config/defaults.yaml')
        config.environment = 'harness'
        config.service = 'test'
        data = {
            'ENVIRONMENT': 'harness',
            'PROVIDERS': {'test': {'foo': 'not-bar'}},
            'NAME': 'test',
        }
        self.assertDictEqual(config.settings.to_dict(), data)

    def test_defaults_with_service(self):
        config = CallyServiceConfig()
        config.config_file = self.get_test_file('config/defaults.yaml')
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
        config = CallyServiceConfig()
        config.config_file = self.get_test_file('config/defaults.yaml')
        config.environment = 'harness'
        config.service = 'defaults'
        data = {
            'NAME': 'defaults',
            'ENVIRONMENT': 'harness',
            'PROVIDERS': {'test': {'foo': 'totally-not-bar'}},
        }
        self.assertDictEqual(config.settings.to_dict(), data)

    def test_mixin_service_win(self):
        config = CallyServiceConfig()
        config.config_file = self.get_test_file('config/mixins.yaml')
        config.environment = 'harness'
        config.service = 'mixy-m-toasus-service'
        data = {
            'ENVIRONMENT': 'harness',
            'NAME': 'mixy-m-toasus-service',
            'STACK_VARS': {'foo': 'mixy'},
        }
        self.assertDictEqual(config.settings.to_dict(), data)

    def test_mixin_env_win(self):
        config = CallyServiceConfig()
        config.config_file = self.get_test_file('config/mixins.yaml')
        config.environment = 'harness'
        config.service = 'mixy-m-toasus-env'
        data = {
            'ENVIRONMENT': 'harness',
            'NAME': 'mixy-m-toasus-env',
            'STACK_VARS': {'foo': 'keith'},
        }
        self.assertDictEqual(config.settings.to_dict(), data)

    def test_mixin_combined(self):
        config = CallyServiceConfig()
        config.config_file = self.get_test_file('config/mixins.yaml')
        config.environment = 'harness'
        config.service = 'mixy-m-toasus-combine'
        data = {
            'ENVIRONMENT': 'harness',
            'NAME': 'mixy-m-toasus-combine',
            'STACK_VARS': {'rattus': 'p rattus', 'foo': 'keith'},
        }
        self.assertDictEqual(config.settings.to_dict(), data)


class CallyServiceConfigValidationTests(CallyTestHarness):
    def test_name_upper_raises(self):
        config = CallyServiceConfig()
        config.config_file = self.get_test_file('config/validation.yaml')
        config.environment = 'harness'
        config.service = 'INVALID-name'
        with self.assertRaises(ValidationError) as context:
            _ = config.settings.name
        self.assertEqual('Name must be lowercase', str(context.exception))

    def test_environment_raises(self):
        config = CallyServiceConfig()
        config.config_file = 'blah.yaml'
        config.environment = 10
        config.service = 'name'
        with self.assertRaises(ValidationError) as context:
            _ = config.settings.name
        self.assertEqual(
            "ENVIRONMENT must is_type_of <class 'str'>, but is: 10",
            str(context.exception),
        )

    def test_stack_vars_not_dict_raises(self):
        config = CallyServiceConfig()
        config.config_file = self.get_test_file('config/validation.yaml')
        config.environment = 'harness'
        config.service = 'invalid-stack-vars'
        with self.assertRaises(ValidationError) as context:
            _ = config.settings.name
        self.assertEqual(
            "STACK_VARS must is_type_of <class 'dict'>, but is: first,second,third",
            str(context.exception),
        )

    def test_providers_not_dict_raises(self):
        config = CallyServiceConfig()
        config.config_file = self.get_test_file('config/validation.yaml')
        config.environment = 'harness'
        config.service = 'invalid-providers'
        with self.assertRaises(ValidationError) as context:
            _ = config.settings.name
        self.assertEqual(
            "PROVIDERS must is_type_of <class 'dict'>, but is: first,second,third",
            str(context.exception),
        )


class CallyServiceConfigTypeTests(CallyTestHarness):
    def test_as_cally_service(self):
        config = CallyServiceConfig()
        config.config_file = Path('blah.yaml')
        config.environment = 'test'
        config.service = 'test'
        self.assertIsInstance(config.config, config_types.CallyService)

    def test_as_cally_stack_service(self):
        config = CallyStackServiceConfig()
        config.config_file = Path('blah.yaml')
        config.environment = 'test'
        config.service = 'test'
        config.settings.stack_type = 'CallyStack'
        self.assertIsInstance(config.config, config_types.CallyStackService)


class CallyEnvironmentConfigTypeTests(CallyTestHarness):
    def test_as_cally_service(self):
        config = CallyEnvironmentConfig()
        config.config_file = Path('blah.yaml')
        config.environment = 'test'
        self.assertIsInstance(config.config, config_types.CallyEnvironment)

    def test_defaults_with_env(self):
        config = CallyEnvironmentConfig()
        config.config_file = self.get_test_file('config/defaults.yaml')
        config.environment = 'harness'
        data = {
            'ENVIRONMENT': 'harness',
            'PROVIDERS': {'test': {'foo': 'not-bar'}},
            'SERVICES': {
                'defaults': {'providers': {'test': {'foo': 'really-not-bar'}}}
            },
        }
        self.assertDictEqual(config.settings.to_dict(), data)
