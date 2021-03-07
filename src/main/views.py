from flask import render_template, session
from . import main

@main.route('/', methods=['GET', 'POST'])
def index():
    user_data = session['user_data'] if 'user_data' in session else {}
    return render_template('index.html',
        is_active={}, user_data=user_data)

@main.route('/projects')
def projects():
    return render_template('projects.html',
        is_active={'projects': True}, user_data=session['user_data'])

@main.route('/issues')
def issues():
    return render_template('issues.html',
        is_active={'issues': True}, user_data=session['user_data'])

@main.route('/messages')
def messages():
    return render_template('messages.html',
        is_active={'messages': True}, user_data=session['user_data'])

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html",
        is_active={}, user_data={}), 404
