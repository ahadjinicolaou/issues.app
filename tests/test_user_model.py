from src.models import User
import pytest

def test_password_setter():
    u = User(password='meep')
    assert u.password_hash is not None

def test_unreadable_password():
    u = User(password='meep')
    with pytest.raises(AttributeError):
        u.password

def test_password_verification():
    u = User(password='meep')
    assert u.verify_password('meep') == True
    assert u.verify_password('beep') == False
