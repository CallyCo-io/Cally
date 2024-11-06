from click.testing import CliRunner

from cally import cli

from .. import CallyIdpTestHarness


class CliTests(CallyIdpTestHarness):

    def test_example(self):
        result = CliRunner().invoke(
            cli.cally,
            ['example', 'hello', 'World'],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello World\n')
