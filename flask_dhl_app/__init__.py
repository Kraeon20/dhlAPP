from flask import Flask

from .routes import home
# , result




def create_app(config_file = "settings.py"):
    app = Flask(__name__)

    app.config.from_pyfile(config_file)

    app.register_blueprint(home)

    return app


