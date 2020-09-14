from setuptools import setup, find_packages


setup(
    name='issues',
    version='0.2',
    packages=find_packages(),
    install_requires=["flask", "pytest", "pytest-flask", "flask-bootstrap"],
)