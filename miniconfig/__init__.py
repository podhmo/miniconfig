# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import pkg_resources
import sys


PHASE1_CONFIG = -20
PHASE2_CONFIG = -10


class ConfigurationError(Exception):
    pass


def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)


def caller_module(level=2):
    module_globals = sys._getframe(level).f_globals
    name = module_globals.get("__name__", "__main__")
    return sys.modules[name]


class ConfiguratorCore(object):
    def __init__(self, settings=None, module=None, queue=None):
        self.settings = settings or {}
        self.module = module or caller_module()
        self.queue = queue or []

    def build_import_symbol_string(self, fn_or_string):
        if not fn_or_string.startswith("."):
            return fn_or_string

        nodes = self.module.__name__.split(".")
        if fn_or_string.endswith("."):
            fn_or_string = fn_or_string[1:]

        for i, c in enumerate(fn_or_string):
            if c != ".":
                break
            nodes.pop()
        if fn_or_string == "" or fn_or_string.endswith("."):
            return ".".join(nodes)
        return ".".join(nodes) + "." + fn_or_string[i:]

    def include(self, fn_or_string):
        if callable(fn_or_string):
            includeme = fn_or_string
            module = None
        else:
            symbol_string = self.build_import_symbol_string(fn_or_string)
            if ":" in symbol_string:
                module_string, fn_name = symbol_string.split(":", 1)
            else:
                module_string, fn_name = symbol_string, "includeme"
            module = import_symbol(module_string)
            includeme = getattr(module, fn_name)

        config = self.__class__(self.settings, module=module, queue=self.queue)
        return includeme(config)

    def action(self, callback, order=0):
        self.queue.append((order, callback))

    def commit(self):
        for o, callback in sorted(self.queue, key=lambda xs: xs[0]):
            callback()
        self.queue = []
