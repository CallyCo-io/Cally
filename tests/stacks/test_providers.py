from contextlib import suppress
from unittest import skipUnless

from cally.cdk import CallyResource, CallyStack

from .. import CallyTfTestHarness

skip_tests = False
with suppress(ModuleNotFoundError):
    from cally.providers.google import pubsub_topic  # noqa: F401
    from cally.providers.random import pet  # noqa: F401

    skip_tests = True


@skipUnless(skip_tests, "Random provider must be installed")
class CallyProviderTests(CallyTfTestHarness):
    def test_provider_load(self):
        stack = CallyStack(service=self.empty_service)

        class Pet(CallyResource):
            provider = 'random'
            resource = 'pet'

        stack.add_resource(Pet('random-pet-name'))
        result = self.synth_stack(stack)
        testdata = self.load_json_file('cdk/provider_load.json')
        self.assertDictEqual(result.get('provider'), testdata.get('provider'))
        self.assertDictEqual(result.get('resource'), testdata.get('resource'))

    def test_provider_config(self):
        self.empty_service.providers.update(random={'alias': 'foo'})
        stack = CallyStack(service=self.empty_service)

        class Pet(CallyResource):
            provider = 'random'
            resource = 'pet'

        stack.add_resource(Pet('random-pet-name'))
        result = self.synth_stack(stack)
        self.assertEqual(
            result.get('provider', {}).get('random', {})[0].get('alias', ''), 'foo'
        )

    def test_resource_identifier(self):
        class Pet(CallyResource):
            provider = 'random'
            resource = 'pet'

        self.assertEqual('${pet.random-pet.id}', str(Pet('random-pet')))

    def test_resource_identifier_underscore(self):
        class PubsubTopic(CallyResource):
            provider = 'google'
            resource = 'pubsub_topic'

        self.assertEqual(
            '${pubsub_topic.random-topic.id}', str(PubsubTopic('random-topic'))
        )
