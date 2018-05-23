# -*- coding:utf-8 -*-
import logging
from functools import partial
from importlib import import_module
import sys
logger = logging.getLogger(__name__)

PHASE1_CONFIG = -20
PHASE2_CONFIG = -10


class ConfigurationError(Exception):
    pass


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
    def __init__(self, settings, queue=None):
        self.settings = settings
        self.queue = queue or []


class ConfiguratorCore(object):
    context_factory = Context

    def __init__(self, settings=None, module=None, context=None):
        self._settings = settings or {}
        self.module = module or caller_module()
        self.context = context or self.context_factory(self._settings)

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tb):
        self.commit()
        return None

    def build_import_path(self, fn_or_string, dont_popping=True):
        if not fn_or_string.startswith("."):
            return fn_or_string

        nodes = self.module.__name__.split(".")
        if fn_or_string.endswith("."):
            fn_or_string = fn_or_string[1:]

        poped = []
        for i, c in enumerate(fn_or_string):
            if c != ".":
                break
            poped.append(nodes.pop())
        if fn_or_string == "" or fn_or_string.endswith("."):
            return ".".join(nodes)

        if dont_popping:
            nodes.append(poped[-1])
        return ".".join(nodes) + "." + fn_or_string[i:]

    def is_init_module(self):
        return "__init__.py" in self.module.__file__

    def include(self, fn_or_string):
        if callable(fn_or_string):
            includeme = fn_or_string
            module = getattr(includeme, "__module__", None)
            module = import_symbol(module)
        else:
            symbol_string = self.build_import_path(fn_or_string, dont_popping=self.is_init_module())
            includeme = import_symbol(symbol_string)
            if not callable(includeme):
                includeme = includeme.includeme
            module = import_symbol(includeme.__module__)

        config = self.__class__(self._settings, module=module, context=self.context)
        return includeme(config)

    def action(self, callback, order=0):
        self.queue.append((order, callback))

    def commit(self):
        for o, callback in sorted(self.queue, key=lambda xs: xs[0]):
            callback()
        self.queue = []

    def maybe_dotted(self, fn_or_string):
        if callable(fn_or_string):
            return fn_or_string
        symbol_string = self.build_import_path(fn_or_string, dont_popping=self.is_init_module())
        return import_symbol(symbol_string)

    def add_directive(self, name, fn_or_string):
        fn = self.maybe_dotted(fn_or_string)
        setattr(self.context, name, fn)

    def __getattr__(self, name):
        attr = getattr(self.context, name)
        if callable(attr):
            return partial(attr, self)
        return attr


# stolen from pyramid
class reify(object):
    """cached property"""

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val
