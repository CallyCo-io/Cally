from cally.cli.config.config_types import CallyService, CallyStackService

from .. import CallyTestHarness


class TestCallyService(CallyTestHarness):
    def test_name(self):
        service = CallyService(name='snoopy', environment='yard')
        self.assertEqual(service.name, 'snoopy')

    def test_environment(self):
        service = CallyService(name='snoopy', environment='yard')
        self.assertEqual(service.name, 'snoopy')


class TestCallyStackService(CallyTestHarness):
    def test_stack_type(self):
        service = CallyStackService(
            name='snoopy', environment='yard', stack_type='CallyStack'
        )
        self.assertEqual(service.stack_type, 'CallyStack')

    def test_provider_empty(self):
        service = CallyStackService(
            name='snoopy', environment='yard', stack_type='CallyStack'
        )
        self.assertDictEqual(service.get_provider_vars('test'), {})

    def test_get_provider_vars(self):
        providers = {'test': {'foo': 'bar', 'bar': 'foo'}, 'another': {'bar': 'foo'}}
        service = CallyStackService(
            name='snoopy',
            environment='yard',
            stack_type='CallyStack',
            providers=providers,
        )
        self.assertDictEqual(
            service.get_provider_vars('test'), {'foo': 'bar', 'bar': 'foo'}
        )

    def test_stack_var_empty(self):
        service = CallyStackService(
            name='snoopy', environment='yard', stack_type='CallyStack'
        )
        self.assertIsNone(service.get_stack_var('test'))

    def test_stack_var_default(self):
        service = CallyStackService(
            name='snoopy', environment='yard', stack_type='CallyStack'
        )
        self.assertEqual(service.get_stack_var('test', 'charlie'), 'charlie')

    def test_default_backend(self):
        service = CallyStackService(
            name='snoopy', environment='yard', stack_type='CallyStack'
        )
        self.assertEqual(service.backend_type, 'LocalBackend')

    def test_default_state_path(self):
        service = CallyStackService(
            name='snoopy', environment='yard', stack_type='CallyStack'
        )
        self.assertDictEqual(service.backend_config, {'path': 'state/yard/snoopy'})

    def test_supplied_backend(self):
        service = CallyStackService(
            name='snoopy',
            environment='yard',
            stack_type='CallyStack',
            backend={'type': 'GcsBackend'},
        )
        self.assertEqual(service.backend_type, 'GcsBackend')

    def test_custom_path(self):
        service = CallyStackService(
            name='snoopy',
            environment='yard',
            stack_type='CallyStack',
            providers={'google': {'project': 'test-project'}},
            backend={
                'path': '{environment}/{providers[google][project]}/{name}',
                'path_key': 'prefix',
                'config': {'bucket': 'BucketyMcBucketFace'},
            },
        )
        self.assertDictEqual(
            service.backend_config,
            {'bucket': 'BucketyMcBucketFace', 'prefix': 'yard/test-project/snoopy'},
        )
