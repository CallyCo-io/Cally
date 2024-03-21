from cally.cli.config import CallyConfig

from ... import CallyIdpTestHarness


class CallyIdpConfigTests(CallyIdpTestHarness):

    def test_idp_defaults(self):
        config = CallyConfig(config_file='blah.yaml')
        config.environment = 'harness'
        config.service = 'idp-defaults-ya'
        data = {
            'ENVIRONMENT': 'harness',
            'NAME': 'idp-defaults-ya',
            'PROVIDERS': {'provido': {'location': 'some-place1'}},
        }
        self.assertDictEqual(config.settings.to_dict(), data)
