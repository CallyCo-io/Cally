from cally import cli
from cally.cli.config import CallyConfig
from click.testing import CliRunner

from .. import CallyIdpTestHarness


class CliTests(CallyIdpTestHarness):

    def test_example(self):
        result = CliRunner().invoke(
            cli.cally,
            ['example', 'hello', 'World'],
            obj=CallyConfig(config_file='blah.yaml'),
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello World\n')
