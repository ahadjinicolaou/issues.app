# run from flask shell
from src import db
from src.models import Role, User, Issue, Project, Message
from src.models import perms as p, status as s
from datetime import datetime, timedelta


def add_roles():
    r1 = Role(name='associate', permissions=p.CREATE_COMMENTS)
    r2 = Role(name='employee', permissions=p.CREATE_COMMENTS + p.CREATE_ISSUES)
    r3 = Role(name='reviewer', permissions=p.CREATE_COMMENTS +
              p.CREATE_ISSUES + p.RESOLVE_ISSUES)
    r4 = Role(name='manager', permissions=p.CREATE_COMMENTS +
              p.CREATE_ISSUES + p.CREATE_PROJECTS + p.ARCHIVE_PROJECTS)
    r5 = Role(name='administrator', permissions=p.EVERYTHING)
    db.session.add_all([r1, r2, r3, r4, r5])
    db.session.commit()


def add_users():
    r1 = Role.query.filter_by(name='employee').first()
    r2 = Role.query.filter_by(name='manager').first()
    u1 = User(username='grover', email='grover@hotmail.com', role_id=r1.id)
    u2 = User(username='ernie', email='ernie@yahoo.com', role_id=r1.id)
    u3 = User(username='bert', email='bert@gmail.com', role_id=r2.id)

    u1.password = 'gleep'
    u2.password = 'rubberducky'
    u3.password = 'pigeon'
    db.session.add_all([u1, u2, u3])
    db.session.commit()


def add_projects():
    u1 = User.query.filter_by(username='grover').first()
    p1 = Project(created_by=u1.id,
                 title='Sesame Street Wikipedia entry', code='SSWIKI', client='Sesame Workshop')
    p2 = Project(created_by=u1.id,
                 title='Cryptocurrency adoption study', code='CRYPTO', client='Corporate')

    db.session.add_all([p1, p2])
    db.session.commit()


def add_issues():
    u1 = User.query.filter_by(username='grover').first()
    u2 = User.query.filter_by(username='ernie').first()
    u3 = User.query.filter_by(username='bert').first()
    p1 = Project.query.filter_by(code='SSWIKI').first()
    p2 = Project.query.filter_by(code='CRYPTO').first()

    i1 = Issue(created_by=u1.id, project_code=p1.code,
               project_id=p1.id, title='Fix TOC')
    i2 = Issue(created_by=u1.id, project_code=p1.code,
               project_id=p1.id, title='Revise Reception section')
    i3 = Issue(created_by=u3.id, project_code=p1.code, project_id=p1.id, title='Add Discography section',
               assigned_to=u2.id, status_code=s.ASSIGNED)

    i4 = Issue(created_by=u3.id, project_code=p2.code, assigned_to=u2.id, status_code=s.ASSIGNED,
               project_id=p1.id, title='BTC case study')
    i5 = Issue(created_by=u3.id, project_code=p2.code,
               project_id=p1.id, title='DOGE case study')
    i6 = Issue(created_by=u3.id, project_code=p2.code,
               project_id=p1.id, title='XRP case study')
    db.session.add_all([i1, i2, i3, i4, i5, i6])
    db.session.commit()


def add_messages():
    u1 = User.query.filter_by(username='grover').first()
    u2 = User.query.filter_by(username='ernie').first()
    u3 = User.query.filter_by(username='bert').first()
    m1 = Message(created_by=u1.id, sent_to=u2.id, body='Could you sort out that scrolling issue?',
                 created_on=datetime.now()-timedelta(hours=3, seconds=55))
    m2 = Message(created_by=u1.id, sent_to=u2.id, body='Hmm maybe it\'s not such a big deal in the end?',
                 created_on=datetime.now()-timedelta(hours=3, seconds=40))
    m3 = Message(created_by=u2.id, sent_to=u1.id, body='On it, just have to finish off some other stuff.',
                 created_on=datetime.now()-timedelta(hours=3, seconds=10))

    m4 = Message(created_by=u2.id, sent_to=u3.id, body='Wanna get lunch soon?',
                 created_on=datetime.now()-timedelta(hours=8, seconds=40))
    m5 = Message(created_by=u3.id, sent_to=u2.id, body='Yeah! Let\'s do burgers!',
                 created_on=datetime.now()-timedelta(hours=8, seconds=25))
    db.session.add_all([m1, m2, m3, m4, m5])
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
