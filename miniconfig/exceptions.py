import typing as t
from .types import CallbackFunction


class ConfigurationError(Exception):
    pass


class Conflict(ConfigurationError):
    def __init__(
        self,
        *args: t.Any,
        prev: t.Optional[CallbackFunction] = None,
        current: t.Optional[CallbackFunction] = None,
    ) -> None:
        self.prev = prev
        self.current = current
        super().__init__(*args)

    def __str__(self) -> str:
        return "{} is already registered, prev={}, current={}".format(
            self.args[0], self.prev, self.current
        )
