from miniconfig import ConfiguratorCore


class Configurator(ConfiguratorCore):
    pass


def add_plugin(config, name, plugin):
    def register():
        config.settings[name] = plugin

    discriminator = (add_plugin, name)
    config.action(discriminator, register)


if __name__ == "__main__":
    config = Configurator()
    config.add_directive("add_plugin", add_plugin)
    config.add_plugin("x", object())
    config.add_plugin("y", object())
    config.add_plugin("x", object())  # conflict
    config.commit()
    print(config.settings)
