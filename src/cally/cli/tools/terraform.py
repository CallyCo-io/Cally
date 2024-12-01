import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from types import TracebackType
from typing import Tuple, Type

from cally.cdk import stacks

from ..config.config_types import CallyStackService


class Action:
    _cwd: Path
    _tmp_dir: TemporaryDirectory
    service: CallyStackService

    def __init__(self, service: CallyStackService) -> None:
        self.service = service

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
        return Path(self.tmp_dir, 'stacks', self.service.name)

    @property
    def output_file(self) -> Path:
        return Path(self.output_path, 'cdk.tf.json')

    def synth_stack(
        self,
    ) -> None:
        # TODO: fix typing here
        cls = getattr(stacks, self.service.stack_type)
        cls(self.service).synth_stack(self.tmp_dir)

    def print(self) -> str:
        self.synth_stack()
        return self.output_file.read_text()


class Command:
    arguments: Tuple[str, ...]
    terraform_path: str
    _result: subprocess.CompletedProcess

    def __init__(self, terraform_path: str, arguments: Tuple[str, ...]) -> None:
        self.terraform_path = terraform_path
        self.arguments = arguments

    @property
    def result(self) -> subprocess.CompletedProcess:
        if getattr(self, '_result', None) is None:
            self._result = subprocess.run(
                args=[self.terraform_path, *self.arguments],
                capture_output=True,
                check=False,
            )
        return self._result

    @property
    def success(self) -> bool:
        return self.result.returncode == 0

    @property
    def returncode(self) -> int:
        return self.result.returncode

    @property
    def stderr(self) -> int:
        return self.result.stderr

    @property
    def stdout(self) -> int:
        return self.result.stdout
