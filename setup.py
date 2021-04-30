from setuptools import setup, find_packages


setup(
    name="issues",
    version="0.5",
    packages=find_packages(),
    install_requires=[
        "flask",
        "pytest",
        "pytest-flask",
        "bootstrap-flask",
        "flask-sqlalchemy",
        "flask-login",
        "flask-mail",
        "flask-wtf",
        "flask-moment",
        "email-validator",
    ],
)
