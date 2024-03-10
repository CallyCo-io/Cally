from cally.cdktf import CallyStack

from .. import CallyTfTestHarness


class CallyStackTests(CallyTfTestHarness):

    def test_empty_synth(self):
        stack = CallyStack('test')
        result = self.synth_stack(stack)
        self.assertDictEqual(result, self.load_json_file('cdktf/empty_synth.json'))
