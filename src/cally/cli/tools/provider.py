import os
import shutil
import subprocess
from pathlib import Path
from string import Template
from tempfile import TemporaryDirectory

from ..constants import PROVIDER_CDKTF, PROVIDER_PYPROJECT


class ProviderBuilder:
    provider: str
    source: str
    version: str

    def __init__(self, source: str, provider: str, version: str) -> None:
        self.source = source
        self.provider = provider
        self.version = version

    @property
    def title(self) -> str:
        return self.provider.title().replace('_', '')

    @property
    def provider_path(self) -> str:
        return f"{self.source}/{self.provider.replace('_', '-')}"

    def build(self, output: Path = Path('build')) -> str:
        build_output = Path(output, self.provider)
        build_path = Path(build_output, 'cally', 'providers')
        build_path.mkdir(parents=True, exist_ok=True)
        cdktf_output = build_path.absolute().as_posix()

        cwd = Path.cwd()
        with TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            Path('cdktf.json').write_text(
                Template(PROVIDER_CDKTF).substitute(
                    provider=self.provider_path,
                    version=self.version,
                    path=cdktf_output,
                )
            )
            cdktf_command = str(shutil.which('cdktf'))

            result = subprocess.run(
                f'{cdktf_command} get', shell=True, check=False, stdout=subprocess.PIPE
            )
            message = f"Generated {self.provider} provider"
            if result.returncode != 0:
                message = f"Failed generating {self.provider} provider"
            command_output = result.stdout.decode('utf8').strip()
            os.chdir(cwd)

        Path(build_output, 'pyproject.toml').write_text(
            Template(PROVIDER_PYPROJECT).substitute(
                title=self.title, version=self.version
            )
        )
        return f'{message}\n\n{command_output}'
