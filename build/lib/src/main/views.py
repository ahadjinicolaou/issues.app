from flask import render_template, session, abort
from flask_login import login_required, current_user
from . import main
from ..models import Role, User, Message, Comment, Issue, Project, db, status, entity


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
    navdata, issues = None, {}
    if current_user.is_authenticated:
        navdata = get_navbar_data()
        all_issues = Issue.query.filter_by(assigned_to=current_user.id).all()

        # sort issues into each category
        statuses = ['ASSIGNED', 'ACCEPTED', 'FIXED']
        for issue in all_issues:
            s = status.name(issue.status_code)
            if s in statuses:
                if s not in issues.keys():
                    issues[s] = []
                issues[s].append(issue)

    return render_template('index.html', navdata=navdata, user=current_user, issues=issues)


@main.route('/projects')
@login_required
def projects():
    projects = Project.query.all()
    navdata = get_navbar_data(active_page='projects')
    return render_template(
        'projects.html', navdata=navdata, user=current_user, projects=projects)


@main.route('/projects/<string:code>')
@login_required
def project(code):
    project = Project.query.filter_by(code=code).first()
    if not project:
        abort(404)
    issues = Issue.query.filter_by(project_id=project.id).all()
    comments = Comment.query.filter_by(
        entity_id=project.id, entity_code=entity['PROJECT']).all()
    print(comments)
    navdata = get_navbar_data(active_page='projects')
    return render_template(
        'project.html', navdata=navdata, user=current_user, project=project, issues=issues, comments=comments)


@main.route('/issues')
@login_required
def issues():
    issues = Issue.query.all()
    navdata = get_navbar_data(active_page='issues')
    return render_template(
        'issues.html', navdata=navdata, user=current_user, issues=issues)


@main.route('/issues/<string:code>')
@login_required
def issue(code):
    id = code.split('-')[1]
    issue = Issue.query.filter_by(id=id).first()
    if not issue:
        abort(404)
    comments = Comment.query.filter_by(
        entity_id=issue.id, entity_code=entity['ISSUE']).all()
    navdata = get_navbar_data(active_page='issues')
    return render_template(
        'issue.html', navdata=navdata, user=current_user, issue=issue, comments=comments)


@main.route('/users/<string:username>')
@login_required
def user(username):
    selected_user = User.query.filter_by(username=username).first()
    if not selected_user:
        abort(404)
    navdata = get_navbar_data(active_page=None)
    return render_template(
        'user.html', navdata=navdata, user=current_user, selected_user=selected_user)


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
