import os
from . import create_app


app = create_app(os.getenv('ISSUES_CONFIG') or 'default')
