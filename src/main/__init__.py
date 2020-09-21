from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from src.main.config import config

from datetime import datetime

bootstrap = Bootstrap()

# factory function
def create_app(config_name):
   app = Flask(__name__, template_folder='../templates', static_folder='../static')
   app.config.from_object(config[config_name])

   bootstrap.init_app(app)

   @app.route('/')
   def index():
      return render_template('dashboard.html',
            is_active={},
            user_data=get_user_data())

   @app.route('/projects')
   def projects():
      return render_template('projects.html',
            is_active={'projects': True},
            user_data=get_user_data())

   @app.route('/issues')
   def issues():
      return render_template('issues.html',
            is_active={'issues': True},
            user_data=get_user_data())

   @app.route('/messages')
   def messages():
      return render_template('messages.html',
            is_active={'messages': True},
            user_data=get_user_data())

   @app.errorhandler(404)
   def page_not_found(e):
      return render_template("404.html",
            is_active={},
            user_data={}), 404

   def get_user_data():
      return {
         'user': 'ahadjinicolaou',
         'role': 'admin',
         'num_issues': 12,
         'num_messages': 2}

   return app
