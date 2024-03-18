from cally.cli.config.types import CallyService, CallyStackService

from .. import CallyTestHarness


class TestCallyService(CallyTestHarness):
    def test_name(self):
        service = CallyService(name='snoopy', environment='yard')
        self.assertEqual(service.name, 'snoopy')

    def test_environment(self):
        service = CallyService(name='snoopy', environment='yard')
        self.assertEqual(service.name, 'snoopy')


class TestCallyStackService(CallyTestHarness):
    def test_provider_empty(self):
        service = CallyStackService(name='snoopy', environment='yard')
        self.assertDictEqual(service.get_provider_vars('test'), {})

    def test_get_provider_vars(self):
        providers = {'test': {'foo': 'bar', 'bar': 'foo'}, 'another': {'bar': 'foo'}}
        service = CallyStackService(
            name='snoopy', environment='yard', providers=providers
        )
        self.assertDictEqual(
            service.get_provider_vars('test'), {'foo': 'bar', 'bar': 'foo'}
        )

    def test_stack_var_empty(self):
        service = CallyStackService(name='snoopy', environment='yard')
        self.assertIsNone(service.get_stack_var('test'))

    def test_stack_var_default(self):
        service = CallyStackService(name='snoopy', environment='yard')
        self.assertEqual(service.get_stack_var('test', 'charlie'), 'charlie')
