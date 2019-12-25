import os
from flask import Flask
from lind.config import config, basedir

VERSION = '1.0.2'


def create_app(config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(__name__)
    app.config.from_object(config)
    config.init_app(app)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    return app


def register(app):
    from lind.main import main
    app.register_blueprint(main)

    from lind.admin import admin
    app.register_blueprint(admin)

    from lind import views
    return app


app = create_app(config)
app = register(app)
