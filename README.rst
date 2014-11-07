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
