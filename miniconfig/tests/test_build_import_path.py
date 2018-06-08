# -*- coding:utf-8 -*-
import pytest


def _callFUT(*args, **kwargs):
    from miniconfig import build_import_path
    return build_import_path(*args, **kwargs)


@pytest.mark.parametrize("current_module, symbol_string, import_symbol", [
    ("foo.bar.boo", "moo", "moo"),
    ("foo.bar.boo", "moo.moo", "moo.moo"),
    ("foo.bar.boo", ".moo", "foo.bar.boo.moo"),
    ("foo.bar.boo", "..moo", "foo.bar.moo"),
    ("foo.bar.boo", ".", "foo.bar.boo"),
    ("foo.bar.boo", "..", "foo.bar"),
])
def test_build_import_path(current_module, symbol_string, import_symbol):
    class module:
        pass
    module = module()
    module.__name__ = current_module
    assert _callFUT(module, symbol_string) == import_symbol


@pytest.mark.parametrize("current_module, symbol_string, import_symbol", [
    ("foo.bar.boo", "moo.Fn", "moo.Fn"),
    ("foo.bar.boo", ".Fn", "foo.bar.Fn"),
    ("foo.bar.boo", ".moo:Fn", "foo.bar.moo:Fn"),
    ("foo.bar.boo", ".moo.Fn", "foo.bar.moo.Fn"),
    ("foo.bar.boo", "..moo:Fn", "foo.moo:Fn"),
])
def test_build_import_path2(current_module, symbol_string, import_symbol):
    class module:
        pass
    module = module()
    module.__name__ = current_module
    assert _callFUT(module, symbol_string, dont_popping=False) == import_symbol

