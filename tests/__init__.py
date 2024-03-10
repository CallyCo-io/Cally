import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock


class CallyTestHarness(TestCase):
    working: TemporaryDirectory

    def setUp(self):
        self.current_working = Path().cwd()
        self.working = TemporaryDirectory()
        self.env_patcher = mock.patch.dict(
            os.environ,
            {
                "HOME": self.working.name,
                "LC_ALL": os.environ.get('LC_ALL', 'C.UTF-8'),
                "LANG": os.environ.get('LANG', 'C.UTF-8'),
            },
            clear=True,
        )
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()
        self.working.cleanup()
        os.chdir(self.current_working)
