# run from flask shell
from src import db
from src.models import Role, User, Issue, Project, Message, Comment
from src.models import Permission as p, Status, Entity, IssueType
from datetime import datetime, date, timedelta


T0 = date(2020, 3, 14)


def add_roles():
    r1 = Role(
        name="associate", permissions=p.MESSAGE_USERS.value + p.CREATE_COMMENTS.value
    )
    r2 = Role(
        name="employee",
        permissions=p.MESSAGE_USERS.value
        + p.CREATE_COMMENTS.value
        + p.CREATE_ISSUES.value,
    )
    r3 = Role(
        name="reviewer",
        permissions=p.MESSAGE_USERS.value
        + p.CREATE_COMMENTS.value
        + p.CREATE_ISSUES.value
        + p.RESOLVE_ISSUES.value,
    )
    r4 = Role(
        name="manager",
        permissions=p.MESSAGE_USERS
        + p.CREATE_COMMENTS.value
        + p.CREATE_ISSUES.value
        + p.CREATE_PROJECTS.value
        + p.ARCHIVE_PROJECTS.value,
    )
    r5 = Role(name="administrator", permissions=p.EVERYTHING.value)
    db.session.add_all([r1, r2, r3, r4, r5])
    db.session.commit()


def add_users():
    admin = Role.query.filter_by(name="administrator").first()
    employee = Role.query.filter_by(name="employee").first()
    reviewer = Role.query.filter_by(name="reviewer").first()
    manager = Role.query.filter_by(name="manager").first()
    u1 = User(
        username="boris",
        email="boris@admin.com",
        full_name="Boris Ivanovich Grishenko",
        company="GE Siberia",
        role_id=admin.id,
    )
    u2 = User(
        username="grover",
        email="grover@hotmail.com",
        full_name="Grover Cleveland",
        company="Sesame Street",
        role_id=employee.id,
    )
    u3 = User(
        username="ernie",
        email="ernie@yahoo.com",
        full_name="Ernie Kovacs",
        company="Sesame Street",
        role_id=employee.id,
    )
    u4 = User(
        username="bert",
        email="bert@gmail.com",
        full_name="Bert Reynolds",
        company="Sesame Street",
        role_id=reviewer.id,
    )
    u5 = User(
        username="kermit",
        email="kermitthefrog@gmail.com",
        full_name="Kermit Ruffins",
        company="Sesame Street",
        role_id=manager.id,
    )

    u1.password = "iaminvincible"
    u2.password = "gleep"
    u3.password = "rubberducky"
    u4.password = "pigeon"
    u5.password = "hi-ho"
    db.session.add_all([u1, u2, u3, u4, u5])
    db.session.commit()


def add_projects():
    u1 = User.query.filter_by(username="grover").first()
    u2 = User.query.filter_by(username="kermit").first()

    p1 = Project(
        created_by=u1.id,
        created_on=T0 + timedelta(days=10),
        code="SSWIKI",
        client="Sesame Workshop",
        title="Sesame Street Wikipedia entry",
        body="A comprehensive description of the eponymous show, complete with character biographies.",
    )
    p2 = Project(
        created_by=u1.id,
        created_on=T0 + timedelta(days=40),
        code="CRYPTO",
        client="Goldman Sachs",
        title="Cryptocurrency adoption survey",
        body="An in-depth review of this relatively young investment class, with an eye towards expanding into alternative markets.",
    )
    p3 = Project(
        created_by=u2.id,
        created_on=T0 + timedelta(days=160),
        code="RAINGEN",
        client="Turnbull Enterprises",
        title="Cloud-seeding feasibility study",
        body="Literature review and basic feasibility write-up for (as yet untested) technology developed by the Australian Rain Corporation.",
    )

    db.session.add_all([p1, p2, p3])
    db.session.commit()


def add_issues():
    u1 = User.query.filter_by(username="grover").first()
    u2 = User.query.filter_by(username="ernie").first()
    u3 = User.query.filter_by(username="bert").first()
    u4 = User.query.filter_by(username="boris").first()
    p1 = Project.query.filter_by(code="SSWIKI").first()
    p2 = Project.query.filter_by(code="CRYPTO").first()
    p3 = Project.query.filter_by(code="RAINGEN").first()

    s_review = Status.REVIEW.value
    s_assigned = Status.ASSIGNED.value

    bug_tcode = IssueType.BUG.value
    todo_tcode = IssueType.TODO.value
    i1 = Issue(
        type_code=bug_tcode,
        created_by=u1.id,
        created_on=p1.created_on + timedelta(hours=1),
        project_code=p1.code,
        project_id=p1.id,
        title="Fix TOC",
        body="The table of contents isn't responsive. Looks like it needs a bit of CSS?",
    )
    i2 = Issue(
        type_code=todo_tcode,
        created_by=u1.id,
        created_on=p1.created_on + timedelta(hours=8),
        project_code=p1.code,
        project_id=p1.id,
        title="Revise Reception section",
        assigned_to=u3.id,
        status_code=s_review,
        body="Emphasize the show's positive ratings nationwide. Find out how well SS did on a global scale.",
    )
    i3 = Issue(
        type_code=todo_tcode,
        created_by=u3.id,
        created_on=p1.created_on + timedelta(days=4),
        project_code=p1.code,
        project_id=p1.id,
        title="Add Discography section",
        body="Miss Piggy insists that we include her album...",
        assigned_to=u2.id,
        status_code=s_review,
    )
    i4 = Issue(
        type_code=todo_tcode,
        created_by=u3.id,
        created_on=p2.created_on + timedelta(days=188),
        project_code=p2.code,
        project_id=p2.id,
        title="BTC case study",
        body="Largest cryptocurrency by market cap. The least volatile crypto asset.",
        assigned_to=u2.id,
        status_code=s_assigned,
    )
    i5 = Issue(
        type_code=todo_tcode,
        created_by=u3.id,
        created_on=p2.created_on + timedelta(days=189),
        project_code=p2.code,
        project_id=p2.id,
        title="DOGE case study",
        body="It's a coin with a dog's face on it. Big hit with zoomers.",
    )
    i6 = Issue(
        type_code=todo_tcode,
        created_by=u3.id,
        created_on=p2.created_on + timedelta(days=189),
        project_code=p2.code,
        project_id=p2.id,
        title="XRP case study",
        body="Long-maligned crypto asset that has been making inroads with its SEC case. Potential dark horse investment?",
    )
    i7 = Issue(
        type_code=todo_tcode,
        created_by=u2.id,
        created_on=p3.created_on + timedelta(days=1),
        project_code=p3.code,
        project_id=p3.id,
        title="Atmosphere ionization lab study",
        assigned_to=u1.id,
        status_code=s_assigned,
        body="Investigate whether the lab results described in Greenberg et al., (2007) are generalizable.",
    )

    db.session.add_all([i1, i2, i3, i4, i5, i6, i7])
    db.session.commit()


def add_messages():
    u1 = User.query.filter_by(username="grover").first()
    u2 = User.query.filter_by(username="ernie").first()
    u3 = User.query.filter_by(username="bert").first()
    m1 = Message(
        created_by=u1.id,
        sent_to=u2.id,
        body="Could you sort out that scrolling issue?",
        created_on=datetime.now() - timedelta(hours=3, seconds=55),
        unread=False,
    )
    m2 = Message(
        created_by=u1.id,
        sent_to=u2.id,
        body="Hmm maybe it's not such a big deal in the end?",
        created_on=datetime.now() - timedelta(hours=3, seconds=40),
        unread=False,
    )
    m3 = Message(
        created_by=u2.id,
        sent_to=u1.id,
        body="On it, just have to finish off some other stuff.",
        created_on=datetime.now() - timedelta(hours=3, seconds=10),
        unread=False,
    )

    m4 = Message(
        created_by=u2.id,
        sent_to=u3.id,
        body="Wanna get food soon?",
        created_on=datetime.now() - timedelta(hours=8, seconds=40),
    )
    m5 = Message(
        created_by=u3.id,
        sent_to=u2.id,
        body="Yeah! Let's do burgers!",
        created_on=datetime.now() - timedelta(hours=8, seconds=25),
    )
    m6 = Message(
        created_by=u3.id,
        sent_to=u1.id,
        body="Food?",
        created_on=datetime.now() - timedelta(hours=8, seconds=2),
    )
    db.session.add_all([m1, m2, m3, m4, m5, m6])
    db.session.commit()


def add_comments():
    u1 = User.query.filter_by(username="ernie").first()
    u2 = User.query.filter_by(username="bert").first()
    u3 = User.query.filter_by(username="kermit").first()
    p1 = Project.query.filter_by(code="SSWIKI").first()
    p2 = Project.query.filter_by(code="CRYPTO").first()
    p3 = Project.query.filter_by(code="RAINGEN").first()
    i1 = Issue.query.filter_by(project_code=p1.code, title="Fix TOC").first()

    # comments on issue
    issue_ecode = Entity.ISSUE.value
    c1 = Comment(
        created_by=u1.id,
        entity_id=i1.id,
        entity_code=issue_ecode,
        body="Does the draft contain everything? Is there more to come?",
        created_on=datetime.now() - timedelta(hours=6, seconds=22),
    )
    c2 = Comment(
        created_by=u2.id,
        entity_id=i1.id,
        entity_code=issue_ecode,
        body="I think they're waiting on a few suggestions.",
        created_on=datetime.now() - timedelta(hours=5, seconds=58),
    )

    # comments on project
    project_ecode = Entity.PROJECT.value
    c3 = Comment(
        created_by=u2.id,
        created_on=p2.created_on + timedelta(hours=1),
        entity_id=p2.id,
        entity_code=project_ecode,
        body="Corporate isn't too keen on DOGE. Just a heads up.",
    )
    c4 = Comment(
        created_by=u1.id,
        created_on=p2.created_on + timedelta(hours=2),
        entity_id=p2.id,
        entity_code=project_ecode,
        body="I just checked, there's some disagreement about how useful it will be but they want us to do a feasibility study anyway.",
    )
    c5 = Comment(
        created_by=u3.id,
        created_on=p2.created_on + timedelta(hours=2, minutes=5),
        entity_id=p2.id,
        entity_code=project_ecode,
        body="It's unknown territory for the whole board. Let's get a prelim out to them ASAP.",
    )
    c6 = Comment(
        created_by=u2.id,
        created_on=p3.created_on + timedelta(hours=1, minutes=20),
        entity_id=p3.id,
        entity_code=project_ecode,
        body="To put it mildly, this study is garbage. How is this a project?",
    )
    c7 = Comment(
        created_by=u3.id,
        created_on=p3.created_on + timedelta(hours=1, minutes=40),
        entity_id=p3.id,
        entity_code=project_ecode,
        body="Well, there's a paying client. Apparently corporate is getting top dollar for this, so we should at least give them something.",
    )

    db.session.add_all([c1, c2, c3, c4, c5, c6, c7])
    db.session.commit()


def regenerate_all():
    # reset database
    db.drop_all()
    db.create_all()
    add_roles()
    add_users()
    add_projects()
    add_issues()
    add_messages()
    add_comments()
