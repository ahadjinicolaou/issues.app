import os
from src import create_app, db
from src.models import Role, User, Issue, Project
from src.models import perms, status
app = create_app(os.getenv('ISSUES_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    # convenience function for flask shell
    return dict(db=db, perms=perms, status=status, Role=Role,
                User=User, Issue=Issue, Project=Project)
