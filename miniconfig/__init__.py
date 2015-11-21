# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from functools import partial
from importlib import import_module
import sys


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


class Control(object):
    def __init__(self, queue=None):
        self.queue = queue or []


class ConfiguratorCore(object):
    def __init__(self, settings=None, module=None, control=None):
        self.settings = settings or {}
        self.module = module or caller_module()
        self.control = control or Control()

    def build_import_symbol_string(self, fn_or_string, dot_is_current_position=True):
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

        if dot_is_current_position:
            nodes.append(poped[-1])
        return ".".join(nodes) + "." + fn_or_string[i:]

    def include(self, fn_or_string):
        if callable(fn_or_string):
            includeme = fn_or_string
            module = getattr(fn_or_string, "__module__", None)
        else:
            symbol_string = self.build_import_symbol_string(fn_or_string)
            includeme = import_symbol(symbol_string)
            if not callable(includeme):
                includeme = includeme.includeme
            module = import_symbol(includeme.__module__)

        config = self.__class__(self.settings,
                                module=module,
                                control=self.control)
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
        symbol_string = self.build_import_symbol_string(fn_or_string, dot_is_current_position=False)
        return import_symbol(symbol_string)

    def add_directive(self, name, fn_or_string):
        fn = self.maybe_dotted(fn_or_string)
        setattr(self.control, name, fn)

    def __getattr__(self, name):
        attr = getattr(self.control, name)
        if callable(attr):
            return partial(attr, self)
        return attr
