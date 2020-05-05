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
    import sys

    def _fake_module(name):
        class module:
            status = [False]

            @classmethod
            def includeme(cls, config):
                cls.status[0] = True

        sys.modules[name] = module()
        return module

    foo = _fake_module("miniconfig.foo")

    config = _getTarget()()
    config.include("miniconfig.foo")
    assert foo.status[0] is True


def test_include__module_with_functioname():
    import sys

    def _fake_module(name):
        class module:
            status = [False]

            @classmethod
            def myincludeme(cls, config):
                cls.status[0] = True

        sys.modules[name] = module
        return module

    boo = _fake_module("miniconfig.boo")

    config = _getTarget()()
    config.include("miniconfig.boo:myincludeme")
    assert boo.status[0] is True
