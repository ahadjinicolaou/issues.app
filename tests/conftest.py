from src.issues import create_app
import pytest


# app instance configured for testing
@pytest.fixture
def app():
    app = create_app('testing')
    return app
