# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

from securityclientpy.version import __version__

setup(
    name='securityserverpy',
    version=__version__,
    author='Jordan Hubbard',
    author_email='jhubb95@yahoo.com',
    description='a python server for the Smart Vehicle Security System',
    packages=find_packages(),
    setup_requires='setuptools',
    install_requires=[
        'xmltodict',
        'PyYAML'
    ],
    entry_points={
        'console_scripts': [
            'securityserverpy=securityserverpy.main:main',
        ]
    }
)