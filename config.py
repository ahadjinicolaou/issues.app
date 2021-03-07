import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') # needed for tamper-proof session cookies
    SQLALCHEMY_TRACK_MODIFICATIONS = False # PYTEST COMPLAINS ABOUT THIS!

class DevelopmentConfig(Config):
    # enables interactive debugger on the development server
    # also useful for monitoring code changes
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True # disables error catching during request handling
    SQLALCHEMY_DATABASE_URI = 'sqlite://' # test data stored in memory

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
