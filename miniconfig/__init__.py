import logging
import sys
from functools import partial
from importlib import import_module
from miniconfig.langhelpers import reify # noqa F401

logger = logging.getLogger(__name__)

PHASE1_CONFIG = -20
PHASE2_CONFIG = -10
ORDER_DEFAULT = 0


class ConfigurationError(Exception):
    pass


class Conflict(ConfigurationError):
    def __init__(self, *args, prev=None, current=None, **kwargs):
        self.prev = prev
        self.current = current
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "{} is already registered, prev={}, current={}".format(
            self.args[0], self.prev, self.current
        )


def import_symbol(symbol):
    if "." not in symbol:
        return import_module(symbol)
    elif ":" in symbol:
        module, attr = symbol.rsplit(":", 1)
        m = import_module(module)
        return getattr(m, attr)
    else:
        module, attr = symbol.rsplit(".", 1)
        m = import_module(module)
        if hasattr(m, attr):
            return getattr(m, attr)
        else:
            return import_module(symbol)


def caller_module(level=2):
    module_globals = sys._getframe(level).f_globals
    name = module_globals.get("__name__", "__main__")
    return sys.modules[name]


class Context(object):
    def __init__(self, settings, queue=None, seen=None):
        self.settings = settings
        self.queue = queue or []
        self.seen = seen or {}


def is_init_module(module):
    return "__init__.py" in module.__file__


def build_import_path(module, path, *, dont_popping=True):
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


def build_import_path_plus(module, path, *, dont_popping=True):
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


class ConfiguratorCore(object):
    context_factory = Context
    build_path = staticmethod(build_import_path_plus)

    def __init__(self, settings=None, module=None, context=None):
        self._settings = settings or {}
        self.module = module or caller_module()
        self.context = context or self.context_factory(self._settings)

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tb):
        self.commit()
        return None

    def include(self, fn_or_string):
        if callable(fn_or_string):
            includeme = fn_or_string
            module = getattr(includeme, "__module__", None)
            module = import_symbol(module)
        else:
            symbol_string = self.build_path(
                self.module, fn_or_string, dont_popping=is_init_module(self.module)
            )
            logger.debug("include %s where %s", symbol_string, self.module)
            includeme = import_symbol(symbol_string)
            if not callable(includeme):
                if not hasattr(includeme, "includeme"):
                    logger.info(
                        "includeme() is not found in %s, where %s",
                        symbol_string,
                        self.module,
                    )
                    return
                includeme = includeme.includeme
            module = import_symbol(includeme.__module__)

        # hack: importing action is only once
        try:
            imported = self.context._imported
        except AttributeError:
            imported = self.context._imported = set()
        if includeme in imported:
            logger.info("%s is already imported, where %s", includeme, self.module)
            return

        imported.add(includeme)

        config = self.__class__(self._settings, module=module, context=self.context)
        return includeme(config)

    def action(self, discriminator, callback, order=ORDER_DEFAULT):
        if discriminator in self.seen:
            raise Conflict(
                discriminator, prev=self.seen[discriminator], current=callback
            )
        self.seen[discriminator] = callback
        self.queue.append((order, callback))

    def commit(self):
        for o, callback in sorted(self.queue, key=lambda xs: xs[0]):
            callback()
        self.queue = []
        self.seen = {}

    def maybe_dotted(self, fn_or_string):
        if callable(fn_or_string):
            return fn_or_string
        symbol_string = self.build_path(
            self.module, fn_or_string, dont_popping=is_init_module(self.module)
        )
        return import_symbol(symbol_string)

    def add_directive(self, name, fn_or_string):
        fn = self.maybe_dotted(fn_or_string)
        setattr(self.context, name, fn)

    def __getattr__(self, name):
        attr = getattr(self.context, name)
        if callable(attr):
            return partial(attr, self)
        return attr
