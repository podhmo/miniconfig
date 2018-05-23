from yourapp import Configurator

config = Configurator()
config.include("yourapp.pluginB")
app = config.make_app()
print(app.settings.keys())  # dict_keys(['A', 'B'])
