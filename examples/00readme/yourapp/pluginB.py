class B:
    pass


def includeme(config):
    config.include(".pluginA")
    config.settings["B"] = B()

