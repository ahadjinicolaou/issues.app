from flask import Blueprint
from flask import render_template


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('dashboard.html',
            is_active={},
            user_data=get_user_data())


@main.route('/projects')
def projects():
    return render_template('projects.html',
            is_active={'projects': True},
            user_data=get_user_data())


@main.route('/issues')
def issues():
    return render_template('issues.html',
            is_active={'issues': True},
            user_data=get_user_data())


@main.route('/messages')
def messages():
    return render_template('messages.html',
            is_active={'messages': True},
            user_data=get_user_data())


@main.app_errorhandler(404)
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
