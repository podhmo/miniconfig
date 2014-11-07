miniconfig
========================================

making configuration phase, in your application.
(Tiny version of almost pyramid's configurator object)

::

    # yourapplication.py
    from miniconfig import ConfiguratorCore

    class Configurator(ConfiguratorCore):
        def make_app(self):
            self.commit()
            return App(self.settings)


pluginA ::

    # yourapplication/pluginA.py

    def includeme(config):
        config.settings["A"] = PluginA()

pluginB ::

    # yourapplication/pluginB.py

    def includeme(config):
        config.include(".pluginA")
        config.settings["B"] = PluginB()


application user ::

    from yourapplication import Configurator
    config = Configurator()
    config.include("yourapplication.pluginB")
    app = config.make_app()


Adding directives
---------------------------------------

directive means that action of configurator.

how to define and use directive ::

    def hello(config, name):
        def register():
            assert config.settings["foo"] == "foo"
            print("hello: {}".format(name))
        config.action(register)


    config = Configurator(settings={"foo": "foo"})
    config.add_directive("hello", hello)
    config.hello("foo")

it is also supported that to define directives by dotted name::

    ## foo/bar.py
    def hello(config):
        def register():
            print("hai")
        config.action(register)

    ## yourapplication
    config = Configurator()
    config.add_directive("hello", "foo.bar:hello")
    config.hello()
    config.commit() # hai

