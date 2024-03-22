import json
import os
from inspect import getfile
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from cally.cdk import CallyStack
from cally.cli.config import CallyConfig

from .constants import HOME_ENVS
from .exceptions import CallyTestingTestdataError


class CallyTestHarness(TestCase):
    working: TemporaryDirectory
    _testdata: Path

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

    @property
    def testdata(self) -> Path:
        if getattr(self, '_testdata', None) is None:
            for parent in Path(getfile(self.__class__)).parents:
                testdata = Path(parent, 'testdata')
                if testdata.exists() and testdata.is_dir():
                    self._testdata = testdata
                    return self._testdata
                if parent.is_dir() and parent.name == 'tests':
                    break
            raise CallyTestingTestdataError(
                "No testdata found, expected structure <project_root>/tests/testdata"
            )
        return self._testdata

    @staticmethod
    def get_cally_config(service='test', environment='cally') -> CallyConfig:
        config = CallyConfig(config_file=Path('not-required.yaml'))
        config.service = service
        config.environment = environment
        return config

    def get_test_file(self, filename) -> Path:
        return Path(self.testdata, filename)

    def load_test_file(self, filename) -> str:
        return self.get_test_file(filename).read_text()

    def load_json_file(self, filename) -> dict:
        return json.loads(self.load_test_file(filename))


class CallyTfTestHarness(CallyTestHarness):

    def synth_stack(self, stack: CallyStack) -> dict:
        stack.synth_stack(self.working.name)
        output_file = Path(self.working.name, 'stacks', stack.name, 'cdk.tf.json')
        return json.loads(output_file.read_text())
