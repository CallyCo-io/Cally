from cally.cli.config.service import CallyServiceConfig

from ... import CallyIdpTestHarness


class CallyIdpConfigTests(CallyIdpTestHarness):

    def test_idp_defaults(self):
        config = CallyServiceConfig()
        config.config_file = 'blah.yaml'
        config.environment = 'harness'
        config.service = 'idp-defaults-ya'
        data = {
            'ENVIRONMENT': 'harness',
            'NAME': 'idp-defaults-ya',
            'PROVIDERS': {'provido': {'location': 'some-place1'}},
        }
        self.assertDictEqual(config.settings.to_dict(), data)
