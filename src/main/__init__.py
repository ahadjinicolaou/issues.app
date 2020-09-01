from flask import Flask
from src.main.config import config


# factory function
def create_app(config_name):
   app = Flask(__name__)
   app.config.from_object(config[config_name])

   # response function for server root
   @app.route('/')
   def index():
      return '<h1>Show me the money!</h1>'

   return app
