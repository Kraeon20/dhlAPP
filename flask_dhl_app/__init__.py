from flask import Flask
from .routes import home





def create_app(config_file = "settings.py"):
    app = Flask(__name__)
    app.secret_key = 'gchjggfgchhjljgu65864684fhgcjtui'


    app.config.from_pyfile(config_file)

    app.register_blueprint(home)

    return app


