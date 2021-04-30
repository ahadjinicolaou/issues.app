from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_required, current_user
from collections import Counter
from . import main
from ..models import Role, User, Message, Comment, Issue, Project, db
from ..models import Status, Entity, Priority, Severity, IssueType
from .forms import (
    AddProjectForm,
    AddIssueForm,
    EditProjectForm,
    EditIssueInfoForm,
    EditIssueStatusForm,
    AssignIssueForm,
    AddCommentForm,
)

ISSUE_STATUS_COLORS = {
    "NEW": "#8ACDEA",
    "ASSIGNED": "#586BA4",
    "ACCEPTED": "#324376",
    "REVIEW": "#F1D302",
    "RESOLVED": "#161925",
    "DISMISSED": "#555555",
}

PROJECT_STATUS_COLORS = {"NEW": "#8ACDEA", "ACTIVE": "#586BA4", "INACTIVE": "#CCCCCC"}


ISSUE_PRIORITY_COLORS = {
    "LOW": "#3f51b5",
    "NORMAL": "#6c757d",
    "HIGH": "#fd7e14",
    "URGENT": "#dc3545",
}


def emojified_issue_type(type_code):
    type = IssueType(type_code)
    return IssueType.emoji(type.name) + " " + type.name.lower()


@login_required
def count_unread_messages():
    return (
        db.session.query(Message)
        .filter(Message.sent_to == current_user.id)
        .filter(Message.unread)
        .count()
    )


@login_required
def count_assigned_issues():
    return (
        db.session.query(Issue)
        .filter(Issue.assigned_to == current_user.id)
        .filter(Issue.status == status["ASSIGNED"])
        .count()
    )


@login_required
def count_assigned_issues():
    return db.session.query(Issue).filter(Issue.assigned_to == current_user.id).count()


@login_required
def get_navbar_data(active_page=None):
    return {
        "active_page": active_page,
        "num_issues": count_assigned_issues(),
        "num_messages": count_unread_messages(),
    }


@main.route("/", methods=["GET", "POST"])
def index():
    navdata, issues = None, {}
    if current_user.is_authenticated:
        navdata = get_navbar_data()
        all_issues = Issue.query.filter_by(assigned_to=current_user.id).all()

        # sort issues into each category
        statuses = ["ASSIGNED", "ACCEPTED", "REVIEW"]
        for issue in all_issues:
            s = Status(issue.status_code).name
            if s in statuses:
                if s not in issues.keys():
                    issues[s] = []
                issues[s].append(issue)

    return render_template(
        "index.html", navdata=navdata, user=current_user, issues=issues, Status=Status
    )


@main.route("/projects")
@login_required
def projects():
    projects = Project.query.all()

    # count the issue statuses
    project_counts = Counter()
    for idx, item in enumerate(projects):
        project_counts[Status(item.status_code).name] += 1
    status_labels = list(project_counts.keys())
    status_counts = list(project_counts.values())
    status_colors = [
        val for (key, val) in PROJECT_STATUS_COLORS.items() if key in status_labels
    ]

    navdata = get_navbar_data(active_page="projects")
    return render_template(
        "projects.html",
        navdata=navdata,
        user=current_user,
        projects=projects,
        status_counts=status_counts,
        status_labels=[x.lower() for x in status_labels],
        status_colors=status_colors,
        Status=Status,
    )


@main.route("/projects/<string:code>")
@login_required
def project(code):
    project = Project.query.filter_by(code=code).first()
    if not project:
        abort(404)

    selected_issue_type = request.args.get("issue_type") or "ALL"
    if selected_issue_type == "ALL":
        issues = Issue.query.filter_by(project_id=project.id).all()
    else:
        issues = Issue.query.filter_by(
            project_id=project.id, type_code=IssueType[selected_issue_type].value
        ).all()

    comments = Comment.query.filter_by(
        entity_id=project.id, entity_code=Entity.PROJECT.value
    ).all()
    navdata = get_navbar_data()
    return render_template(
        "project.html",
        navdata=navdata,
        user=current_user,
        project=project,
        issues=issues,
        selected_issue_type=selected_issue_type,
        issue_emojis=IssueType.emojis(),
        comments=comments,
        Status=Status,
        Entity=Entity,
        IssueType=IssueType,
    )


@main.route("/add_issue", methods=["GET", "POST"])
@login_required
def add_issue():
    # check for valid project code
    code = request.args.get("code")
    navdata = get_navbar_data()
    project = Project.query.filter_by(code=code).first()
    if not project:
        abort(404)

    # initialize issue form data
    form = AddIssueForm(priority=Priority.NORMAL.value, severity=Severity.NORMAL.value)
    form.type_code.choices = [
        (item.value, IssueType.emojified_name(item)) for item in IssueType
    ]
    form.priority.choices = [(item.value, item.name.lower()) for item in Priority]
    form.severity.choices = [(item.value, item.name.lower()) for item in Severity]

    if form.validate_on_submit():
        i = Issue(
            type_code=form.type_code.data,
            created_by=current_user.id,
            project_code=project.code,
            project_id=project.id,
            title=form.title.data,
            body=form.body.data,
            status_code=Status.NEW.value,
            priority_code=form.priority.data,
            severity_code=form.severity.data
        )
        db.session.add(i)
        db.session.commit()

        flash(f"Issue {i.code} added to database.")
        return redirect(url_for(".project", code=code))

    return render_template(
        "add_issue.html", navdata=navdata, user=current_user, project=project, form=form
    )


@main.route("/add_project", methods=["GET", "POST"])
@login_required
def add_project():
    navdata = get_navbar_data()
    form = AddProjectForm()

    if form.validate_on_submit():
        p = Project(
            created_by=current_user.id,
            title=form.title.data,
            body=form.body.data,
            code=form.code.data,
            client=form.client.data,
        )
        db.session.add(p)
        db.session.commit()
        flash(f"Project {p.code} added to database.")
        return redirect(url_for(".projects"))

    return render_template(
        "add_project.html",
        navdata=navdata,
        user=current_user,
        Status=Status,
        Priority=Priority,
        form=form,
    )


@main.route("/add_comment", methods=["GET", "POST"])
@login_required
def add_comment():
    entity_code = request.args.get("entity_code", type=int)
    entity_id = request.args.get("entity_id", type=int)
    form = AddCommentForm()
    navdata = get_navbar_data()

    # check for valid entity
    entity = None
    if Entity(entity_code) == Entity.ISSUE:
        entity = Issue.query.filter_by(id=entity_id).first()
        url = url_for(".issue", code=entity.code)
    elif Entity(entity_code) == Entity.PROJECT:
        entity = Project.query.filter_by(id=entity_id).first()
        url = url_for(".project", code=entity.code)
    if not entity:
        abort(404)

    if form.validate_on_submit():
        c = Comment(
            created_by=current_user.id,
            entity_code=entity_code,
            entity_id=entity_id,
            body=form.body.data,
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url)

    return render_template(
        "add_comment.html",
        navdata=navdata,
        user=current_user,
        form=form,
        entity_code=entity_code,
        entity_id=entity_id,
    )


@main.route("/edit_issue_info", methods=["GET", "POST"])
@login_required
def edit_issue_info():
    issue_id = request.args.get("id", type=int)
    issue = Issue.query.filter_by(id=issue_id).first()

    # initialize issue form data
    form = EditIssueInfoForm(
        type_code=issue.type_code,
        title=issue.title,
        body=issue.body,
    )
    form.type_code.choices = [
        (item.value, IssueType.emojified_name(item)) for item in IssueType
    ]

    if form.validate_on_submit():
        issue.type_code = form.type_code.data
        issue.title = form.title.data
        issue.body = form.body.data

        db.session.commit()
        flash(f"Issue {issue.code} has been updated.")
        return redirect(url_for(".issue", code=issue.code))

    return render_template(
        "edit_issue_info.html",
        navdata=get_navbar_data(),
        user=current_user,
        form=form,
        issue=issue,
    )


@main.route("/edit_issue_status", methods=["GET", "POST"])
@login_required
def edit_issue_status():
    issue_id = request.args.get("id", type=int)
    issue = Issue.query.filter_by(id=issue_id).first()

    # initialize issue form data
    form = EditIssueStatusForm(
        status=issue.status_code,
        priority=issue.priority_code,
        severity=issue.severity_code,
    )
    form.status.choices = [(item.value, item.name) for item in Status]
    form.priority.choices = [(item.value, item.name.lower()) for item in Priority]
    form.severity.choices = [(item.value, item.name.lower()) for item in Severity]

    if form.validate_on_submit():
        issue.status_code = form.status.data
        issue.priority_code = form.priority.data
        issue.severity_code = form.severity.data
        db.session.commit()

        flash(f"Issue {issue.code} has been updated.")
        return redirect(url_for(".issue", code=issue.code))

    return render_template(
        "edit_issue_status.html",
        navdata=get_navbar_data(),
        user=current_user,
        form=form,
        issue=issue,
    )


@main.route("/assign_issue", methods=["GET", "POST"])
@login_required
def assign_issue():
    issue_id = request.args.get("id", type=int)
    issue = Issue.query.filter_by(id=issue_id).first()
    id = issue.id or None

    # initialize issue form data
    form = AssignIssueForm(
        assignee=id,
    )
    form.assignee.choices = User.query.with_entities(User.id, User.username).all()

    if form.validate_on_submit():
        assignee = User.query.filter_by(id=form.assignee.data).first()
        issue.assigned_to = form.assignee.data
        db.session.commit()

        flash(f"Issue {issue.code} has been assigned to {assignee.username}.")
        return redirect(url_for(".issue", code=issue.code))

    return render_template(
        "assign_issue.html",
        navdata=get_navbar_data(),
        user=current_user,
        form=form,
        issue=issue,
    )


@main.route("/edit_project", methods=["GET", "POST"])
@login_required
def edit_project():
    navdata = get_navbar_data()
    project_id = request.args.get("id", type=int)
    project = Project.query.filter_by(id=project_id).first()

    form = EditProjectForm(
        code=project.code, client=project.client, title=project.title, body=project.body
    )

    if form.validate_on_submit():
        project.code = form.code.data
        project.client = form.client.data
        project.title = form.title.data
        project.body = form.body.data
        db.session.commit()
        flash(f"Project {project.code} updated.")
        return redirect(url_for(".project", code=project.code))

    return render_template(
        "edit_project.html",
        navdata=navdata,
        user=current_user,
        form=form,
        project=project,
    )


@main.route("/issues")
@login_required
def issues():
    selected_issue_type = request.args.get("issue_type") or "ALL"
    if selected_issue_type not in IssueType.names() and selected_issue_type != "ALL":
        abort(404)

    # count the issue statuses
    if selected_issue_type == "ALL":
        issues = Issue.query.all()
    else:
        issues = Issue.query.filter_by(
            type_code=IssueType[selected_issue_type].value
        ).all()

    labels, counts, colors = {}, {}, {}
    labels["status"], counts["status"] = issue_property_counts(
        issues, property="status"
    )
    labels["priority"], counts["priority"] = issue_property_counts(
        issues, property="priority"
    )

    colors["status"] = [
        val for (key, val) in ISSUE_STATUS_COLORS.items() if key in labels["status"]
    ]
    colors["priority"] = [
        val for (key, val) in ISSUE_PRIORITY_COLORS.items() if key in labels["priority"]
    ]

    navdata = get_navbar_data(active_page="issues")
    return render_template(
        "issues.html",
        navdata=navdata,
        user=current_user,
        issues=issues,
        IssueType=IssueType,
        selected_issue_type=selected_issue_type,
        issue_emojis=IssueType.emojis(),
        status_labels=[x.lower() for x in labels["status"]],
        status_counts=counts["status"],
        status_colors=colors["status"],
        priority_labels=[x.lower() for x in labels["priority"]],
        priority_counts=counts["priority"],
        priority_colors=colors["priority"],
        Status=Status,
    )


def issue_property_counts(issues, property="status"):
    counts = Counter()
    for idx, item in enumerate(issues):
        if property == "status":
            counts[Status(item.status_code).name] += 1
        elif property == "priority":
            counts[Priority(item.priority_code).name] += 1
        else:
            raise Exception(f"Unhandled issue property: {property}")
    return list(counts.keys()), list(counts.values())


@main.route("/issues/<string:code>")
@login_required
def issue(code):
    id = code.split("-")[1]
    issue = Issue.query.filter_by(id=id).first()
    if not issue:
        abort(404)
    comments = Comment.query.filter_by(
        entity_id=issue.id, entity_code=Entity.ISSUE.value
    ).all()
    navdata = get_navbar_data()
    return render_template(
        "issue.html",
        navdata=navdata,
        user=current_user,
        issue=issue,
        comments=comments,
        Entity=Entity,
    )


@main.route("/users/<string:username>")
@login_required
def user(username):
    selected_user = User.query.filter_by(username=username).first()
    if not selected_user:
        abort(404)
    navdata = get_navbar_data()
    return render_template(
        "user.html", navdata=navdata, user=current_user, selected_user=selected_user
    )


@main.route("/messages")
@login_required
def messages():
    navdata = get_navbar_data(active_page="messages")
    others = db.session.query(User).filter(User.id != current_user.id).all()
    messages = (
        db.session.query(Message)
        .filter(
            (Message.created_by == current_user.id)
            | (Message.sent_to == current_user.id)
        )
        .all()
    )
    return render_template(
        "messages.html",
        navdata=navdata,
        user=current_user,
        others=others,
        messages=messages,
    )


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html", is_active={}, user_data={}), 404
