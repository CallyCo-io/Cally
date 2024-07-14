from click.testing import CliRunner

from cally import cli
from cally.cli.config.service import CallyServiceConfig

from .. import CallyIdpTestHarness


class CliTests(CallyIdpTestHarness):

    def test_example(self):
        result = CliRunner().invoke(
            cli.cally,
            ['example', 'hello', 'World'],
            obj=CallyServiceConfig(config_file='blah.yaml'),
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello World\n')
