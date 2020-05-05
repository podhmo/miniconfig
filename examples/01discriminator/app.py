import typing as t
from miniconfig import ConfiguratorCore


class Configurator(ConfiguratorCore):
    pass


def add_plugin(config: Configurator, name: str, plugin: t.Any) -> None:
    def register() -> None:
        config.settings[name] = plugin

    discriminator = (add_plugin.__name__, name)
    config.action(discriminator, register)


if __name__ == "__main__":
    config = Configurator()
    config.add_directive("add_plugin", add_plugin)
    config.add_plugin("x", object())
    config.add_plugin("y", object())
    config.add_plugin("x", object())  # conflict
    config.commit()
    print(config.settings)
