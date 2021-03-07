from setuptools import setup, find_packages


setup(
    name='issues',
    version='0.4',
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
        "email-validator"],
)