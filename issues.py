import os
from src import create_app


app = create_app(os.getenv('ISSUES_CONFIG') or 'default')
