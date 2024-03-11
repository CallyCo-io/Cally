from cally.cli.tools.provider import ProviderBuilder

from .. import CallyTestHarness


class ProviderBuilderTests(CallyTestHarness):

    def test_title(self):
        self.assertEqual(
            ProviderBuilder(
                source='hashicorp', provider='random', version='3.6.0'
            ).title,
            'Random',
        )

    def test_provider_path(self):
        self.assertEqual(
            ProviderBuilder(
                source='hashicorp', provider='random', version='3.6.0'
            ).provider_path,
            'hashicorp/random',
        )
