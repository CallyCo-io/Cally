import os
from unittest import mock

from click.testing import CliRunner

from cally.cli.commands.config import print_service
from cally.cli.config import CallyConfig

from .. import CallyTestHarness


class ConfigCliTests(CallyTestHarness):
    @mock.patch.dict(os.environ, {"CALLY_STACK_TYPE": "CallyStack"})
    def test_print_service_basic(self):
        result = CliRunner().invoke(
            print_service,
            ['--service', 'test-cli', '--environment', 'test'],
            obj=CallyConfig(config_file='blah.yaml'),
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            'ENVIRONMENT: test\nNAME: test-cli\nSTACK_TYPE: CallyStack\n\n',
        )
