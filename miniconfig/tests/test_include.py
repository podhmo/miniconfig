# -*- coding:utf-8 -*-
import pytest


def _getTarget():
    from miniconfig import ConfiguratorCore
    return ConfiguratorCore


@pytest.mark.parametrize("current_module, symbol_string, import_symbol", [
    ("foo.bar.boo", "moo", "moo"),
    ("foo.bar.boo", "moo.moo", "moo.moo"),
    ("foo.bar.boo", ".moo", "foo.bar.moo"),
    ("foo.bar.boo", "..moo", "foo.moo"),
    ("foo.bar.boo", ".", "foo.bar.boo"),
    ("foo.bar.boo", "..", "foo.bar"),
])
def test_build_import_symbol_string(current_module, symbol_string, import_symbol):
    class module:
        pass
    config = _getTarget()(module=module())
    config.module.__name__ = current_module
    assert config.build_import_symbol_string(symbol_string) == import_symbol


def test_include__function():
    status = [False]

    def includeme(config):
        status[0] = True

    config = _getTarget()()
    config.include(includeme)
    assert status[0] is True


def test_include__module():
    import imp
    import sys

    status = [False]

    def includeme(config):
        status[0] = True

    module = imp.new_module("miniconfig.foo")
    module.includeme = includeme
    sys.modules["miniconfig.foo"] = module

    config = _getTarget()()
    config.include("miniconfig.foo")
    assert status[0] is True


def test_include__module_with_functioname():
    import imp
    import sys

    status = [False]

    def includeme(config):
        status[0] = True

    module = imp.new_module("miniconfig.boo")
    module.myincludeme = includeme
    sys.modules["miniconfig.boo"] = module

    config = _getTarget()()
    config.include("miniconfig.boo:myincludeme")
    assert status[0] is True
