import typing as t
import logging
from functools import partial
from types import ModuleType

from miniconfig.types import CallbackFunction
from miniconfig.modulelib import (  # noqa F401
    import_symbol,
    caller_module,
    is_init_module,
    build_import_path,
    build_import_path_plus,
)
from miniconfig.exceptions import (  # noqa F401
    ConfigurationError,
    Conflict,
)
from miniconfig.langhelpers import reify  # noqa F401

logger = logging.getLogger(__name__)

PHASE1_CONFIG = -20
PHASE2_CONFIG = -10
ORDER_DEFAULT = 0


Discriminator = t.Union[str, t.Tuple[str, ...]]
ConfiguratorT = t.TypeVar("ConfiguratorT", bound="ConfiguratorCore")
ContextT = t.TypeVar("ContextT", bound="Context")
IncludeFunction = t.Callable[[ConfiguratorT], t.Any]


# TODO: use dataclasses?
class Context:
    def __init__(
        self,
        settings: t.Optional[t.Dict[str, t.Any]] = None,
        *,
        queue: t.Optional[t.List[t.Tuple[int, CallbackFunction]]] = None,
        seen: t.Optional[t.Dict[Discriminator, CallbackFunction]] = None,
    ) -> None:
        self.settings = settings
        self.queue = queue or []
        self.seen = seen or {}

    @reify
    def imported(self) -> t.Set[t.Any]:
        return set()


class Configurator:
    context_factory = Context
    build_path = staticmethod(build_import_path_plus)

    def __init__(
        self,
        settings: t.Optional[t.Dict[str, t.Any]] = None,
        *,
        module: t.Optional[ModuleType] = None,
        context: t.Optional[ContextT] = None,
    ):
        self._settings = settings or {}
        self.module: ModuleType = module or caller_module()
        self.context: ContextT = context or self.context_factory(  # type:ignore
            self._settings
        )

    def __enter__(self: ConfiguratorT) -> ConfiguratorT:
        return self

    def __exit__(
        self,
        exc: t.Optional[t.Type[BaseException]],
        value: t.Optional[BaseException],
        tb: t.Any,
    ) -> None:
        self.commit()
        return None

    def include(self, fn_or_string: t.Union[t.Callable[..., t.Any], str]) -> t.Any:
        if callable(fn_or_string):
            includeme = fn_or_string
            module = getattr(includeme, "__module__", None)
            module = import_symbol(module)
        else:
            symbol_string = self.build_path(
                self.module, fn_or_string, dont_popping=is_init_module(self.module)
            )
            logger.debug("include %s where %s", symbol_string, self.module)
            includeme_or_module = import_symbol(symbol_string)

            if callable(includeme_or_module):
                includeme = includeme_or_module
            else:
                if not hasattr(includeme_or_module, "includeme"):
                    logger.info(
                        "includeme() is not found in %s, where %s",
                        symbol_string,
                        self.module,
                    )
                    return
                includeme = includeme_or_module.includeme  # type: ignore

            module = import_symbol(includeme.__module__)

        # hack: importing action is only once
        imported = self.context.imported
        if includeme in imported:
            logger.info("%s is already imported, where %s", includeme, self.module)
            return

        imported.add(includeme)

        config = self.__class__(self._settings, module=module, context=self.context)
        return includeme(config)

    def action(
        self,
        discriminator: Discriminator,
        callback: CallbackFunction,
        *,
        order: int = ORDER_DEFAULT,
    ) -> None:
        if discriminator in self.context.seen:
            raise Conflict(
                discriminator, prev=self.context.seen[discriminator], current=callback
            )
        self.context.seen[discriminator] = callback
        self.context.queue.append((order, callback))

    def commit(self) -> None:
        for o, callback in sorted(self.context.queue, key=lambda xs: xs[0]):
            callback()

    def maybe_dotted(
        self, fn_or_string: t.Union[t.Callable[..., t.Any], str]
    ) -> t.Union[ModuleType, t.Callable[..., t.Any]]:
        if callable(fn_or_string):
            return fn_or_string
        symbol_string = self.build_path(
            self.module, fn_or_string, dont_popping=is_init_module(self.module)
        )
        return import_symbol(symbol_string)

    def add_directive(
        self, name: str, fn_or_string: t.Union[t.Callable[..., t.Any], str]
    ) -> None:
        fn = self.maybe_dotted(fn_or_string)
        setattr(self.context, name, fn)

    def __getattr__(self, name: str) -> t.Any:
        attr = getattr(self.context, name)
        if callable(attr):
            return partial(attr, self)
        return attr


# for backward compatibility
ConfiguratorCore = Configurator
