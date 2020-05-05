def _getTarget():
    from miniconfig import ConfiguratorCore

    return ConfiguratorCore


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
