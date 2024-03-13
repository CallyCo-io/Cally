import sys
from importlib import reload
from pathlib import Path

sys.path.append(Path(Path(__file__).parent, '../testdata/test_cls').as_posix())

from cally.cdk import stacks

from .. import CallyTfTestHarness


class IdpStackTests(CallyTfTestHarness):
    def setUp(self):
        super().setUp()
        reload(stacks)

    def test_class_load(self):
        self.assertEqual(stacks.MinimalStack.__name__, 'MinimalStack')

    def test_empty_synth(self):
        stack = stacks.MinimalStack('test')
        result = self.synth_stack(stack)
        self.assertDictEqual(result, self.load_json_file('cdktf/empty_synth.json'))
