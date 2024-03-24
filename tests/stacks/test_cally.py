from cally.cdk.stacks import CallyStack

from .. import CallyTfTestHarness


class CallyStackTests(CallyTfTestHarness):

    def test_empty_synth(self):
        stack = CallyStack(service=self.empty_service)
        result = self.synth_stack(stack)
        self.assertDictEqual(
            result.get('terraform'), self.load_json_file('cdk/empty_synth.json')
        )

    def test_gcs_backend(self):
        service = self.empty_service
        service.backend = {
            'type': 'GcsBackend',
            'path_key': 'prefix',
            'path': 'water/{environment}/{name}',
            'config': {'bucket': 'BucketyMcBucketFace'},
        }
        stack = CallyStack(service=service)
        result = self.synth_stack(stack)
        self.assertDictEqual(
            result.get('terraform'), self.load_json_file('cdk/gcs_backend.json')
        )
