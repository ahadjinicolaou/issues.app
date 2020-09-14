from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from src.main.config import config

from datetime import datetime

bootstrap = Bootstrap()

# factory function
def create_app(config_name):
   app = Flask(__name__, template_folder='../templates')
   app.config.from_object(config[config_name])

   bootstrap.init_app(app)

   @app.route('/')
   def index():
      return '<h1>Show me the money!</h1>'

   @app.route('/greeting/<name>')
   def greeting(name):
      return render_template('greeting.html', name=name)

   @app.route('/fancy-greeting/<name>')
   def fancy_greeting(name):
      return render_template('fancy_greeting.html',
            name=name,
            hour=datetime.now().hour)

   @app.errorhandler(404)
   def not_found(e):
      return "<h1>Looks like I can't find that page...</h1>", 404

   return app
