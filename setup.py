#!/usr/bin/env python
import re

from setuptools import setup, find_packages


VERSION = ''
with open('infermedica_api/__init__.py', 'r') as f:
    VERSION = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

long_description = """
    The Infermedica Python client provides access to powerful medical diagnostic API created by Infermedica.

    README and Samples - https://github.com/infermedica/python-api

    Developer portal - https://developer.infermedica.com

    API Reference - https://developer.infermedica.com/docs/api
    """

setup(
    name='infermedica-api',
    version=VERSION,
    description='The Infermedica Python client for Infermedica API.',
    long_description=long_description,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    keywords='infermedica medical api library rest http',
    author='Infermedica',
    author_email='office@infermedica.com',
    url='https://github.com/infermedica/python-api',
    license='Apache 2.0',
    packages=find_packages(exclude=['examples']),
    install_requires=['requests>=1.0.0'],
)
