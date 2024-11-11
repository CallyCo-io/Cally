import json
import os
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

from cally.cli.commands.tf import tf

from .. import CallyTestHarness


class TfTests(CallyTestHarness):

    @mock.patch.dict(os.environ, {"CALLY_STACK_TYPE": "CallyStack"})
    def test_empty_print(self):
        result = CliRunner().invoke(
            tf,
            ['print', '--service', 'test', '--environment', 'test'],
        )
        self.assertEqual(result.exit_code, 0)
        testdata = {"backend": {"local": {"path": "state/test/test"}}}
        self.assertDictEqual(
            json.loads(result.output).get('terraform'),
            testdata,
        )

    @mock.patch.dict(os.environ, {"CALLY_STACK_TYPE": "CallyStack"})
    def test_empty_write(self):
        data = Path(self.working.name, 'cdk.tf.json')
        result = CliRunner().invoke(
            tf,
            [
                'write',
                '--service',
                'test',
                '--environment',
                'test',
                '--output',
                data.as_posix(),
            ],
        )
        self.assertEqual(result.exit_code, 0)
        testdata = {"backend": {"local": {"path": "state/test/test"}}}
        self.assertDictEqual(
            json.loads(data.read_text(encoding='utf8')).get('terraform'),
            testdata,
        )
