from flask import render_template, session
from flask_login import login_required, current_user
from . import main
from ..models import Role, User, Message, Issue, Project, db, status


@login_required
def count_unread_messages():
    return db.session.query(Message) \
        .filter(Message.sent_to == current_user.id) \
        .filter(Message.unread).count()


@login_required
def count_assigned_issues():
    return db.session.query(Issue) \
        .filter(Issue.assigned_to == current_user.id) \
        .filter(Issue.status == status['ASSIGNED']).count()


@login_required
def count_assigned_issues():
    return db.session.query(Issue) \
        .filter(Issue.assigned_to == current_user.id).count()


@login_required
def get_navbar_data(active_page=None):
    return {'active_page': active_page,
            'num_issues': count_assigned_issues(),
            'num_messages': count_unread_messages()}


@main.route('/', methods=['GET', 'POST'])
def index():
    navdata = get_navbar_data() if current_user.is_authenticated else None
    return render_template('index.html', navdata=navdata, user=current_user)


@main.route('/projects')
@login_required
def projects():
    projects = Project.query.all()
    navdata = get_navbar_data(active_page='projects')
    return render_template(
        'projects.html', navdata=navdata, user=current_user, projects=projects)


@main.route('/issues')
@login_required
def issues():
    issues = Issue.query.all()
    navdata = get_navbar_data(active_page='issues')
    return render_template(
        'issues.html', navdata=navdata, user=current_user, issues=issues)


@main.route('/messages')
@login_required
def messages():
    navdata = get_navbar_data(active_page='messages')
    others = db.session.query(User).filter(User.id != current_user.id).all()
    messages = db.session.query(Message) \
        .filter((Message.created_by == current_user.id) | (Message.sent_to == current_user.id)).all()
    return render_template(
        'messages.html', navdata=navdata, user=current_user, others=others, messages=messages)


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html", is_active={}, user_data={}), 404
