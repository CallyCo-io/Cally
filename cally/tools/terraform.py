import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import TracebackType
from typing import Type

from ..cdktf import stacks


class Action:
    _cwd: Path
    _tmp_dir: TemporaryDirectory
    stack_name: str
    stack_type: str

    def __init__(self, stack_name: str, stack_type: str) -> None:
        self.stack_name = stack_name
        self.stack_type = stack_type

    def __enter__(self) -> 'Action':
        self._tmp_dir = TemporaryDirectory()
        self._cwd = Path().cwd()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        os.chdir(self._cwd)
        self._tmp_dir.cleanup()

    @property
    def tmp_dir(self) -> str:
        return self._tmp_dir.name

    @property
    def output_path(self) -> Path:
        return Path(self.tmp_dir, 'stacks', self.stack_name)

    @property
    def output_file(self) -> Path:
        return Path(self.output_path, 'cdk.tf.json')

    def synth_stack(
        self,
    ) -> None:
        # TODO: fix typing here
        cls = getattr(stacks, self.stack_type)
        cls(self.stack_name).synth_stack(self.tmp_dir)

    def print(self) -> str:
        self.synth_stack()
        return self.output_file.read_text()
