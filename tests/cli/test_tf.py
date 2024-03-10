import json

from click.testing import CliRunner


from cally.commands.tf import tf

from .. import CallyTestHarness


class TfTests(CallyTestHarness):

    def test_empty_print(self):
        result = CliRunner().invoke(
            tf, ['print', '--stack-name', 'test-cli', '--stack-type', 'CallyStack']
        )
        self.assertEqual(result.exit_code, 0)
        self.assertDictEqual(
            json.loads(result.output), self.load_json_file('cli/empty_print.json')
        )
