[![Build Status](https://travis-ci.org/podhmo/miniconfig.svg?branch=master)](https://travis-ci.org/podhmo/miniconfig)

# miniconfig


making configuration phase, in your application.
(Tiny version of almost pyramid's configurator object)

```python
# yourapp/__init__.py
from miniconfig import ConfiguratorCore


class Configurator(ConfiguratorCore):
    def make_app(self):
        self.commit()
        return App(self.settings)


class App:
    def __init__(self, settings):
        self.settings = settings
```

yourapp/pluginA.py

```python
class A:
    pass


def includeme(config):
    config.settings["A"] = A()
```

yourapp/pluginB.py

```python
class B:
    pass


def includeme(config):
    config.include(".pluginA")
    config.settings["B"] = B()
```

application user

```python
from yourapp import Configurator

config = Configurator()
config.include("yourapp.pluginB")
app = config.make_app()
print(app.settings.keys())  # dict_keys(['A', 'B'])
```

## Adding directives

directive means that action of configurator.

how to define and use directive

```python
def hello(config, name):
    def register():
        assert config.settings["foo"] == "foo"
        print("hello: {}".format(name))
    discriminator = (hello, name)
    config.action(discriminator, register)


config = Configurator(settings={"foo": "foo"})
config.add_directive("hello", hello)
config.hello("foo")
```

it is also supported that to define directives by dotted name

foo/bar.py

```python
def hello(config):
    def register():
        print("hai")
    discriminator = id(object())  # xxx
    config.action(discriminator, register)
```

yourapp

```python
config = Configurator()
config.add_directive("hello", "foo.bar:hello")
config.hello()
config.commit() # hai
```