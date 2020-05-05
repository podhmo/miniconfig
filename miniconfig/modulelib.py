import typing as t
import sys
from types import ModuleType
from importlib import import_module


def import_symbol(symbol: str) -> t.Union[ModuleType, t.Callable[..., t.Any]]:
    if "." not in symbol:
        return import_module(symbol)
    elif ":" in symbol:
        module, attr = symbol.rsplit(":", 1)
        m = import_module(module)
        return getattr(m, attr)  # type: ignore
    else:
        module, attr = symbol.rsplit(".", 1)
        m = import_module(module)
        if hasattr(m, attr):
            return getattr(m, attr)  # type: ignore
        else:
            return import_module(symbol)


def caller_module(*, level: int = 2) -> ModuleType:
    module_globals = sys._getframe(level).f_globals
    name = module_globals.get("__name__", "__main__")
    return sys.modules[name]


def is_init_module(module: ModuleType) -> bool:
    return "__init__.py" in module.__file__


def build_import_path(
    module: ModuleType, path: str, *, dont_popping: bool = True
) -> str:
    # examples:
    # - foo
    # - foo.bar.boo
    # - .foo
    # - ..foo
    if not path.startswith("."):
        return path

    nodes = module.__name__.split(".")
    if path.endswith("."):
        path = path[1:]

    poped = []
    for i, c in enumerate(path):
        if c != ".":
            break
        poped.append(nodes.pop())
    if path == "" or path.endswith("."):
        return ".".join(nodes)

    if dont_popping:
        nodes.append(poped[-1])
    return ".".join(nodes) + "." + path[i:]


def build_import_path_plus(
    module: ModuleType, path: str, *, dont_popping: bool = True
) -> str:
    # examples:
    # - foo
    # - foo.bar.boo
    # - .foo
    # - ..foo
    # +
    # - ./foo -> .foo
    # - ../foo -> ..foo
    # - ./foo/bar/boo -> foo.bar.boo
    # - ../foo/bar -> ..foo.bar
    if path.startswith("."):
        if module.__name__ == "__main__":
            path = path.replace("./", "", 1)
        else:
            path = path.replace("./", ".", 1)
    path = path.replace("/", ".")
    return build_import_path(module, path, dont_popping=dont_popping)
