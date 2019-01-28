#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package metadata
NAME = 'conspiracy'
DESCRIPTION = 'Automated web app hacking.'
URL = 'https://github.com/gingeleski/conspiracy'
EMAIL = 'rjg26247@gmail.com'
AUTHOR = 'Randy Gingeleski'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1'

# What packages are required for this module to be executed?
REQUIRED = [
    'appdirs', 'asn1crypto', 'cffi', 'cryptography',
    'idna', 'nassl', 'pycparser', 'pyee',
    'pyppeteer', 'python-nmap', 'six', 'sslyze',
    'tls-parser', 'tqdm', 'urllib3', 'websockets',
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long description
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dict
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """
    Supports setup.py upload
    """

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass
        self.status('Building Source and Wheel (universal) distribution...')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))
        self.status('Uploading the package to PyPI via Twine...')
        os.system('twine upload dist/*')
        self.status('Pushing git tags...')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')
        sys.exit()


# Where the magic happens
setup(
    name = NAME,
    version = about['__version__'],
    description = DESCRIPTION,
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = AUTHOR,
    author_email = EMAIL,
    python_requires = REQUIRES_PYTHON,
    url = URL,
    packages = find_packages(exclude=('test',)),
    # If your package is a single module, use this instead of 'packages':
    # py_modules = ['mypackage'],
    # entry_points = {
    #     'console_scripts' : ['mycli=mymodule:cli'],
    # },
    install_requires = REQUIRED,
    extras_require = EXTRAS,
    include_package_data = True,
    license = 'MIT',
    classifiers = [
        # Trove classifiers https://pypi.python.org/pypi?%3Aaction=list_classifiers
        # TODO add Trove classifier for LICENSE once that's situated
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass = {
        'upload' : UploadCommand,
    },
)
