import os
from src import create_app, db
from src.models import User

app = create_app(os.getenv('ISSUES_CONFIG') or 'default')

# convenience function for flask shell
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)