# type: ignore
def _getTarget():
    from miniconfig import ConfiguratorCore

    return ConfiguratorCore


def test_directive__action_is_added():
    def do_action(config):
        pass

    config = _getTarget()()

    assert hasattr(config, "do_action") is False
    config.add_directive("do_action", do_action)
    assert hasattr(config, "do_action") is True


def test_directive__define_by_dottedname():
    import sys

    def _fake_module(name):
        class module:
            finished = [False]

            @classmethod
            def do_action(cls, config):
                cls.finished[0] = True

        sys.modules[name] = module
        return module

    moo = _fake_module("miniconfig.moo")

    config = _getTarget()()
    config.add_directive("do_action", "miniconfig.moo:do_action")
    assert hasattr(config, "do_action") is True

    config.do_action()
    assert moo.finished[0] is True


def test_directive__action_with_config():
    m = object()
    finished = [False]

    def with_me(config):
        assert config.settings["m"] == m
        finished[0] = True

    config = _getTarget()(settings={"m": m})
    config.add_directive("with_me", with_me)

    config.with_me()

    assert finished[0] is True


def test_directive__action_with_arguments():
    collection = []
    finished = [False]

    def add_item(config, x):
        collection.append(x)
        finished[0] = True

    config = _getTarget()()
    config.add_directive("add_item", add_item)

    config.add_item(10)
    config.add_item(200)

    assert finished[0] is True
    assert collection == [10, 200]


def test_directive__sub_configurator_also_same_context():
    config = _getTarget()()
    finished = [False]

    def includeme(config2):
        assert config2.hello() == "hello"
        finished[0] = True

    def hello(config):
        return "hello"

    config.add_directive("hello", hello)
    config.include(includeme)

    assert finished[0] is True
    assert config.hello() == "hello"


def test_directive__sub_configurator_also_same_context2():
    from miniconfig import Context

    class WithHelloContext(Context):
        def hello(self, config):
            return "hello"

    config = _getTarget()(context=WithHelloContext())
    finished = [False]

    def includeme(config2):
        assert config2.hello() == "hello"
        finished[0] = True

    config.include(includeme)
    assert finished[0] is True
    assert config.hello() == "hello"
