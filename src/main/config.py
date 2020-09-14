import os


class Config:
    # needed for tamper-proof session cookies
    SECRET_KEY = os.environ.get('SECRET_KEY')


class DevelopmentConfig(Config):
    # enables interactive debugger on the development server
    # also useful for monitoring code changes
    DEBUG = True


class TestingConfig(Config):
    # disables error catching during request handling
    TESTING = True


class ProductionConfig(Config):
    # to be populated when needed
    PLACEHOLDER = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
