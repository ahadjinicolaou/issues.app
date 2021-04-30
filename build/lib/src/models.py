from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Permission(dict):
    def __init__(self):
        self['NOTHING'] = 0
        self['CREATE_COMMENTS'] = 1
        self['CREATE_ISSUES'] = 2
        self['CREATE_PROJECTS'] = 4
        self['RESOLVE_ISSUES'] = 8
        self['ARCHIVE_PROJECTS'] = 16
        self['EVERYTHING'] = 32

    def __getattr__(self, attr):
        return self.get(attr)

    def name(self, code):
        for key, val in self.items():
            if val == code:
                return key
        # complain if code is absent
        raise KeyError('input is not a valid permission code')


class Status(dict):
    # based on https://developers.google.com/issue-tracker/concepts/issues
    def __init__(self):
        self['NEW'] = 1
        self['ASSIGNED'] = 2
        self['ACCEPTED'] = 3
        self['FIXED'] = 4
        self['RESOLVED'] = 5
        self['DISMISSED'] = 6
        self['ACTIVE'] = 7
        self['INACTIVE'] = 8
        self['ARCHIVED'] = 9

    def __getattr__(self, attr):
        return self.get(attr)

    def name(self, code):
        for key, val in self.items():
            if val == code:
                return key
        # complain if code is absent
        raise KeyError('input is not a valid status code')


class Entity(dict):
    def __init__(self):
        self['ISSUE'] = 1
        self['PROJECT'] = 2
        self['FORUM'] = 3

    def __getattr__(self, attr):
        return self.get(attr)

    def name(self, code):
        for key, val in self.items():
            if val == code:
                return key
        # complain if code is absent
        raise KeyError('input is not a valid entity code')


perms = Permission()
status = Status()
entity = Entity()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    permissions = db.Column(db.Integer, default=perms.NOTHING)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    username = db.Column(db.String(32), unique=True,
                         index=True, nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    company = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f'<User {self.username} [{self.role}]>'

    @property
    def role(self):
        return Role.query.filter_by(id=self.id).first().name

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    status_code = db.Column(
        db.Integer, default=status.INACTIVE, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text)
    code = db.Column(db.String(8), unique=True, nullable=False)
    client = db.Column(db.String(256))
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime)
    started_on = db.Column(db.DateTime, nullable=True)
    projected_end_on = db.Column(db.DateTime, nullable=True)
    ended_on = db.Column(db.DateTime, nullable=True)

    @property
    def status(self):
        return status.name(self.status_code).lower()

    def __repr__(self):
        return f'<Project {self.code} [{status.name(self.status_code)}]>'


class Issue(db.Model):
    __tablename__ = 'issues'
    id = db.Column(db.Integer, primary_key=True)
    status_code = db.Column(db.Integer, default=status.NEW, nullable=False)
    project_code = db.Column(db.String(8), db.ForeignKey(
        'projects.code'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'projects.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime)

    assignee = db.relationship(
        'User', backref='issue_assignee', foreign_keys=[assigned_to])
    creator = db.relationship(
        'User', backref='issue_creator', foreign_keys=[created_by])

    @property
    def code(self):
        return f'{self.project_code}-{self.id}'

    @property
    def status(self):
        return status.name(self.status_code).lower()

    def __repr__(self):
        return f'<Issue {self.code} [{self.status}]>'


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    sent_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    unread = db.Column(db.Boolean, default=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime)

    author = db.relationship(
        'User', backref='message_author', foreign_keys=[created_by])
    recipient = db.relationship(
        'User', backref='message_recipient', foreign_keys=[sent_to])

    def __repr__(self):
        return f'<Message {self.id}>'


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    entity_code = db.Column(db.Integer, nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime)

    author = db.relationship(
        'User', backref='comment_author', foreign_keys=[created_by])
    updater = db.relationship(
        'User', backref='comment_updater', foreign_keys=[updated_by])

    @property
    def entity(self):
        return status.name(self.entity_code).lower()

    def __repr__(self):
        return f'<Comment {self.id}>'
