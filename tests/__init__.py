import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from cally.cdk import CallyStack
from cally.cli.config.types import CallyStackService

from .constants import HOME_ENVS


class CallyTestHarness(TestCase):
    working: TemporaryDirectory

    def setUp(self):
        self.current_working = Path().cwd()
        self.working = TemporaryDirectory()
        self.env_patcher = mock.patch.dict(
            os.environ,
            {
                HOME_ENVS.get(os.name, 'UNKNOWN'): self.working.name,
                "LC_ALL": os.environ.get('LC_ALL', 'C.UTF-8'),
                "LANG": os.environ.get('LANG', 'C.UTF-8'),
            },
            clear=True,
        )
        self.env_patcher.start()
        os.chdir(self.working.name)

    def tearDown(self):
        self.env_patcher.stop()
        os.chdir(self.current_working)
        self.working.cleanup()

    @staticmethod
    def get_test_file(filename) -> Path:
        return Path(Path(__file__).parent, 'testdata', filename)

    def load_test_file(self, filename) -> str:
        return self.get_test_file(filename).read_text()

    def load_json_file(self, filename) -> dict:
        return json.loads(self.load_test_file(filename))


class CallyTfTestHarness(CallyTestHarness):

    def setUp(self):
        super().setUp()
        self.empty_service = CallyStackService(
            name='test', environment='cally', stack_type='CallyStack'
        )

    def synth_stack(self, stack: CallyStack) -> dict:
        stack.synth_stack(self.working.name)
        output_file = Path(self.working.name, 'stacks', stack.name, 'cdk.tf.json')
        return json.loads(output_file.read_text())
