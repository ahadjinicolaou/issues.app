from . import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import IntEnum


class Permission(IntEnum):
    NOTHING = 0
    MESSAGE_USERS = 1
    CREATE_COMMENTS = 2
    CREATE_ISSUES = 4
    CREATE_PROJECTS = 8
    RESOLVE_ISSUES = 16
    ARCHIVE_PROJECTS = 32
    EVERYTHING = 64


class Status(IntEnum):
    NEW = 1
    ASSIGNED = 2
    ACCEPTED = 3
    REVIEW = 4
    RESOLVED = 5
    DISMISSED = 6
    ACTIVE = 7
    INACTIVE = 8
    ARCHIVED = 9


class Entity(IntEnum):
    ISSUE = 1
    PROJECT = 2
    FORUM = 3


ISSUE_TYPE_EMOJIS = {"BUG": "🐛", "TODO": "☑️", "REQUEST": "🎁", "REPORT": "📋"}


class IssueType(IntEnum):
    BUG = 1
    TODO = 2
    REQUEST = 3
    REPORT = 4

    def emoji(name):
        return ISSUE_TYPE_EMOJIS[name]

    def emojis():
        return ISSUE_TYPE_EMOJIS

    def names():
        return [item.name for item in IssueType]

    def codes():
        return [item.value for item in IssueType]

    def emojified_name(input):
        # expects either a type instance or a string
        name = input.name if isinstance(input, IssueType) else input
        return IssueType.emoji(name) + " " + name.lower()


class Priority(IntEnum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class Severity(IntEnum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    EXTREME = 4


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    permissions = db.Column(db.Integer, default=Permission.NOTHING.value)

    def has_permission(self, permission):
        return self.permissions & permission.value == permission.value


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    username = db.Column(db.String(32), unique=True, index=True, nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    company = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f"<User {self.username} [{self.role}]>"

    @property
    def role(self):
        return Role.query.filter_by(id=self.role_id).first().name

    @property
    def password(self):
        raise AttributeError("password is not readable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def can(self, permission):
        return self.role.has_permission(permission)

    def is_admin(self):
        return self.role.has_permission(Permission.EVERYTHING)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return false

    def is_admin(self):
        return false


login_manager.anonymous_user = AnonymousUser


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    status_code = db.Column(db.Integer, default=Status.NEW.value, nullable=False)
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
        return Status(self.status_code).name

    def __repr__(self):
        return f"<Project {self.code} [{Status(self.status_code).name}]>"


class Issue(db.Model):
    __tablename__ = "issues"
    id = db.Column(db.Integer, primary_key=True)
    type_code = db.Column(db.Integer, nullable=False)
    status_code = db.Column(db.Integer, default=Status.NEW.value, nullable=False)
    priority_code = db.Column(db.Integer, default=Priority.NORMAL.value, nullable=False)
    severity_code = db.Column(db.Integer, default=Severity.NORMAL.value, nullable=False)
    project_code = db.Column(
        db.String(8), db.ForeignKey("projects.code"), nullable=False
    )
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime)

    assignee = db.relationship(
        "User", backref="issue_assignee", foreign_keys=[assigned_to]
    )
    creator = db.relationship(
        "User", backref="issue_creator", foreign_keys=[created_by]
    )
    updater = db.relationship(
        "User", backref="issue_updater", foreign_keys=[updated_by]
    )

    @property
    def code(self):
        return f"{self.project_code}-{self.id}"

    @property
    def type_name(self):
        return IssueType(self.type_code).name

    @property
    def type_emoji(self):
        return IssueType.emoji(self.type_name)

    @property
    def emojified_name(self):
        return IssueType.emojified_name(self.type_name)

    @property
    def status(self):
        return Status(self.status_code).name

    @property
    def severity(self):
        return Severity(self.severity_code).name

    @property
    def priority(self):
        return Priority(self.priority_code).name

    def __repr__(self):
        return f"<Issue {self.code} [{Status(self.status_code).name}]>"


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    sent_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    body = db.Column(db.Text)
    unread = db.Column(db.Boolean, default=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime)

    author = db.relationship(
        "User", backref="message_author", foreign_keys=[created_by]
    )
    recipient = db.relationship(
        "User", backref="message_recipient", foreign_keys=[sent_to]
    )

    def __repr__(self):
        return f"<Message {self.id}>"


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    body = db.Column(db.Text)
    entity_code = db.Column(db.Integer, nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime)

    author = db.relationship(
        "User", backref="comment_author", foreign_keys=[created_by]
    )
    updater = db.relationship(
        "User", backref="comment_updater", foreign_keys=[updated_by]
    )

    def __repr__(self):
        return f"<Comment {self.id}>"
