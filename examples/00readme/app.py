from yourapp import Configurator

config = Configurator()
config.include("yourapp.pluginB")
app = config.make_app()
print(list(app.settings.keys()))  # ['A', 'B']
