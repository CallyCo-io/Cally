import sys
from importlib import reload
from pathlib import Path

sys.path.append(Path(Path(__file__).parent, '../testdata/test_cls').as_posix())

from cally import cli
from cally.cli.config import CallyConfig
from click.testing import CliRunner

from .. import CallyTestHarness


class CliTests(CallyTestHarness):
    def setUp(self):
        super().setUp()
        reload(cli)

    def test_example(self):
        result = CliRunner().invoke(
            cli.cally,
            ['example', 'hello', 'World'],
            obj=CallyConfig(config_file='blah.yaml'),
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello World\n')
