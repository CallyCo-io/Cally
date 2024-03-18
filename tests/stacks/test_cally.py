from cally.cdk.stacks import CallyStack

from .. import CallyTfTestHarness


class CallyStackTests(CallyTfTestHarness):

    def test_empty_synth(self):
        stack = CallyStack(service=self.empty_service)
        result = self.synth_stack(stack)
        self.assertDictEqual(result, self.load_json_file('cdk/empty_synth.json'))
