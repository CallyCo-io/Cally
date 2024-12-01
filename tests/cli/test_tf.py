import json
import os
from pathlib import Path
from unittest import mock, skipUnless

from click.testing import CliRunner

from cally.cli.commands.tf import tf

from .. import CallyTestHarness

SKIP_TESTS = Path(os.environ.get('CALLY_TERRAFORM_PATH', '.not-set')).is_file()


class TfActionTests(CallyTestHarness):

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


@skipUnless(SKIP_TESTS, "CALLY_TERRAFORM_PATH must be set and valid")
@mock.patch.dict(
    os.environ,
    {
        "CALLY_TERRAFORM_PATH": os.environ.get('CALLY_TERRAFORM_PATH', '.not-set'),
        "CALLY_STACK_TYPE": "CallyStack",
    },
)
class TfCommandTests(CallyTestHarness):
    def test_terraform_version(self):
        result = CliRunner().invoke(
            tf, ['run', 'version', '--environment', 'test', '--service', 'test']
        )
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.output.startswith('Terraform v'))

    def test_terraform_error(self):
        result = CliRunner().invoke(
            tf, ['run', 'invalid-foo', '--environment', 'test', '--service', 'test']
        )
        self.assertEqual(result.exit_code, 1)
        self.assertTrue(
            result.output.startswith('Terraform has no command named "invalid-foo".')
        )
