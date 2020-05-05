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
            self.args[0], _fullname(self.prev), _fullname(self.current)
        )


def _fullname(fn: t.Optional[CallbackFunction]) -> str:
    if fn is None:
        return str(None)
    xs: t.List[str] = []

    if hasattr(fn, "__module__"):
        xs.append(fn.__module__)

    xs.append(
        getattr(fn, "__qualname__", None) or getattr(fn, "__name__", None) or str(fn)
    )
    return ".".join(xs)
