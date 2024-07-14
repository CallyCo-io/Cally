import json
import os
from unittest import mock

from cally.cli.commands.tf import tf
from cally.cli.config.service import CallyServiceConfig
from click.testing import CliRunner

from .. import CallyTestHarness


class TfTests(CallyTestHarness):

    @mock.patch.dict(os.environ, {"CALLY_STACK_TYPE": "CallyStack"})
    def test_empty_print(self):
        result = CliRunner().invoke(
            tf,
            ['print', '--service', 'test', '--environment', 'test'],
            obj=CallyServiceConfig(config_file='blah.yaml'),
        )
        self.assertEqual(result.exit_code, 0)
        testdata = {"backend": {"local": {"path": "state/test/test"}}}
        self.assertDictEqual(
            json.loads(result.output).get('terraform'),
            testdata,
        )
