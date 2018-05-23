class A:
    pass


def includeme(config):
    config.settings["A"] = A()
