import importlib.util
import sys
from pathlib import Path

from cally.testing import CallyTestHarness
from cally.testing.exceptions import CallyTestingTestdataError


class CallyTestingTests(CallyTestHarness):

    def test_testdata_raises(self):
        testpath = Path('tests')
        testpath.mkdir()
        self.get_test_file('testing/no_testdata.py').read_text()
        output = Path(testpath, 'no_testdata.py')
        output.write_text(self.get_test_file('testing/no_testdata.py').read_text())
        spec = importlib.util.spec_from_file_location("no_testdata", output)
        no_testdata = importlib.util.module_from_spec(spec)
        sys.modules["no_testdata"] = no_testdata
        spec.loader.exec_module(no_testdata)
        with self.assertRaises(CallyTestingTestdataError):
            _ = no_testdata.NoTestData().testdata
