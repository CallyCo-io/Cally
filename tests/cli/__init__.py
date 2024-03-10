from click.testing import CliRunner

from cally import __version__
from cally.cli import cally

from .. import CallyTestHarness


class CliTests(CallyTestHarness):

    def test_version(self):
        result = CliRunner().invoke(cally, ['--version'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, f'cally, version {__version__}\n')
