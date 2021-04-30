import os
from src import create_app, db
from src.models import Role, User, Issue, Project
from src.models import Permission, Status, Entity

app = create_app(os.getenv("ISSUES_CONFIG") or "default")


@app.shell_context_processor
def make_shell_context():
    # convenience function for flask shell
    return dict(
        db=db,
        Permission=Permission,
        Status=Status,
        Entity=Entity,
        Role=Role,
        User=User,
        Issue=Issue,
        Project=Project,
    )
