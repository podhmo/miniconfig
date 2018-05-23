from miniconfig import ConfiguratorCore


class Configurator(ConfiguratorCore):
    def make_app(self):
        self.commit()
        return App(self.settings)


class App:
    def __init__(self, settings):
        self.settings = settings
