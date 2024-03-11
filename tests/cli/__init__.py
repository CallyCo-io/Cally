from cally.cli import __version__, cally
from click.testing import CliRunner

from .. import CallyTestHarness


class CliTests(CallyTestHarness):

    def test_version(self):
        result = CliRunner().invoke(cally, ['--version'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, f'cally, version {__version__}\n')
