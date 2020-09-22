from flask import Flask
from flask import Blueprint
from flask import render_template
from flask_bootstrap import Bootstrap
from datetime import datetime
from config import config
from src.main import main


bootstrap = Bootstrap()


# factory function
def create_app(config_name):
    app = Flask(__name__, template_folder='./templates', static_folder='./static')
    app.config.from_object(config[config_name])

    bootstrap.init_app(app)

    from src.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
