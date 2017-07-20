from setuptools import setup, find_packages
from ui import __version__

setup(
    name='django-blurmin',
    version=__version__,
    packages=find_packages(),
    description="An open source admin panel building platform built using "
                "the Django framework.",
    long_description=open("README.rst", 'rb').read().decode('utf-8'),
    install_requires=[
        'Django >= 1.10, < 1.12'
    ],
    include_package_data=True,
)

