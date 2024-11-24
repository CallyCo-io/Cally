from contextlib import suppress
from types import MappingProxyType
from unittest import skipUnless

from cally.cdk import CallyResource, CallyStack

from .. import CallyTfTestHarness

skip_tests = False
with suppress(ModuleNotFoundError):
    from cally.providers.google import pubsub_topic  # noqa: F401
    from cally.providers.random import pet  # noqa: F401

    skip_tests = True


@skipUnless(skip_tests, "Providers must be installed")
class CallyResourceTests(CallyTfTestHarness):
    def test_resource_links(self):
        stack = CallyStack(service=self.empty_service)

        class StorageBucket(CallyResource):
            provider = 'google'
            resource = 'storage_bucket'
            defaults = MappingProxyType({'location': 'AUSTRALIA-SOUTHEAST1'})

        bucket_chips = StorageBucket('bucket', name='chips')
        bucket_fish = StorageBucket('bucketo', name='fish', depends_on=[bucket_chips])
        stack.add_resources([bucket_chips, bucket_fish])
        result = self.synth_stack(stack)
        self.assertEqual(
            result.get('resource', {})
            .get('google_storage_bucket', {})
            .get('bucketo', {})
            .get('depends_on', []),
            ["google_storage_bucket.bucket"],
        )

    def test_resource_attribute(self):
        stack = CallyStack(service=self.empty_service)

        class StorageBucketVersioning(CallyResource):
            provider = 'google'
            resource = 'storage_bucket'
            defaults = MappingProxyType({'enabled': True})

        class StorageBucket(CallyResource):
            provider = 'google'
            resource = 'storage_bucket'
            defaults = MappingProxyType({'location': 'AUSTRALIA-SOUTHEAST1'})

        stack.add_resource(
            StorageBucket('bucketo', name='fish', versioning=StorageBucketVersioning())
        )
        result = self.synth_stack(stack)
        self.assertDictEqual(
            result.get('resource', {})
            .get('google_storage_bucket', {})
            .get('bucketo', {})
            .get('versioning', {}),
            {'enabled': True},
        )

    def test_resource_attribute_list(self):
        stack = CallyStack(service=self.empty_service)

        class StorageBucketLifecycleRule(CallyResource):
            provider = 'google'
            resource = 'storage_bucket'

        class StorageBucketLifecycleRuleAction(CallyResource):
            provider = 'google'
            resource = 'storage_bucket'
            defaults = MappingProxyType({'type': 'Delete'})

        class StorageBucketLifecycleRuleCondition(CallyResource):
            provider = 'google'
            resource = 'storage_bucket'
            defaults = MappingProxyType(
                {'days_since_noncurrent_time': 30, 'with_state': 'ARCHIVED'}
            )

        class StorageBucket(CallyResource):
            provider = 'google'
            resource = 'storage_bucket'
            defaults = MappingProxyType({'location': 'AUSTRALIA-SOUTHEAST1'})

        stack.add_resource(
            StorageBucket(
                'bucketo',
                name='fish',
                lifecycle_rule=[
                    StorageBucketLifecycleRule(
                        condition=StorageBucketLifecycleRuleCondition(),
                        action=StorageBucketLifecycleRuleAction(),
                    )
                ],
            )
        )
        result = self.synth_stack(stack)
        self.assertEqual(
            result.get('resource', {})
            .get('google_storage_bucket', {})
            .get('bucketo', {})
            .get('lifecycle_rule', {}),
            [
                {
                    'action': {'type': 'Delete'},
                    'condition': {
                        'days_since_noncurrent_time': 30,
                        'with_state': 'ARCHIVED',
                    },
                }
            ],
        )

    def test_data_resource_reference_id(self):
        class DataGoogleStorageBucket(CallyResource):
            provider = 'google'
            resource = 'data_google_storage_bucket'
            defaults = MappingProxyType({'location': 'AUSTRALIA-SOUTHEAST1'})

        self.assertEqual(
            str(DataGoogleStorageBucket('bucketo', name='fish')),
            '${data.google_storage_bucket.bucketo.id}',
        )

    def test_data_resource_reference(self):
        class DataGoogleStorageBucket(CallyResource):
            provider = 'google'
            resource = 'data_google_storage_bucket'
            defaults = MappingProxyType({'location': 'AUSTRALIA-SOUTHEAST1'})

        self.assertEqual(
            DataGoogleStorageBucket('bucketo', name='fish').name,
            '${data.google_storage_bucket.bucketo.name}',
        )

    def test_resource_reference_id(self):
        class StorageBucket(CallyResource):
            provider = 'google'
            resource = 'storage_bucket'
            defaults = MappingProxyType({'location': 'AUSTRALIA-SOUTHEAST1'})

        self.assertEqual(
            str(StorageBucket('bucketo', name='fish')),
            '${google_storage_bucket.bucketo.id}',
        )

    def test_resource_reference(self):
        class StorageBucket(CallyResource):
            provider = 'google'
            resource = 'storage_bucket'
            defaults = MappingProxyType({'location': 'AUSTRALIA-SOUTHEAST1'})

        self.assertEqual(
            StorageBucket('bucketo', name='fish').name,
            '${google_storage_bucket.bucketo.name}',
        )

    def test_resource_reference_underscore(self):
        class PubsubTopic(CallyResource):
            provider = 'google'
            resource = 'pubsub_topic'

        self.assertEqual(
            '${google_pubsub_topic.random-topic.id}', str(PubsubTopic('random-topic'))
        )
