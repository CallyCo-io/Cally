import sys
from importlib import import_module, reload
from pathlib import Path

from cally import testing
from cally.cli.config.types import CallyStackService


class CallyTestHarness(testing.CallyTestHarness):
    pass


class CallyTfTestHarness(testing.CallyTfTestHarness):
    def setUp(self):
        super().setUp()
        self.empty_service = CallyStackService(
            name='test', environment='cally', stack_type='CallyStack'
        )


class CallyIdpTestHarness(CallyTfTestHarness):
    def setUp(self):
        sys.path.append(Path(Path(__file__).parent, 'testdata/test_cls').as_posix())
        self.reload_cally_modules()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        sys.path.remove(Path(Path(__file__).parent, 'testdata/test_cls').as_posix())
        for mod in [
            'cally.idp',
            'cally.idp.defaults',
            'cally.idp.stacks',
            'cally.idp.commands',
        ]:
            if mod in sys.modules:
                del sys.modules[mod]
        self.reload_cally_modules()

    @staticmethod
    def reload_cally_modules():
        modules = [
            'cally.cli',
            'cally.cdk.stacks',
            'cally.cli.config.loader',
            'cally.cli.config',
        ]
        for module in modules:
            mod = import_module(module)
            reload(mod)
