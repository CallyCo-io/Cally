from cally.cdk import stacks

from .. import CallyIdpTestHarness


class IdpStackTests(CallyIdpTestHarness):
    def test_class_load(self):
        self.assertEqual(stacks.MinimalStack.__name__, 'MinimalStack')

    def test_empty_synth(self):
        stack = stacks.MinimalStack(service=self.empty_service)
        result = self.synth_stack(stack)
        self.assertDictEqual(
            result.get('terraform'), self.load_json_file('cdk/empty_synth.json')
        )
