from typing import Optional


class CallyEnvironment:
    _environment: Optional[str] = None

    @property
    def environment(self) -> Optional[str]:
        return self._environment

    @environment.setter
    def environment(self, value: str):
        self._environment = value


class CallyService(CallyEnvironment):
    _service: Optional[str]

    @property
    def service(self) -> Optional[str]:
        return self._service

    @service.setter
    def service(self, value: str):
        self._service = value
