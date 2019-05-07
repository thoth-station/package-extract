#!/usr/bin/env python3

import os
from setuptools import setup
from pathlib import Path


def get_requirements():
    with open('requirements.txt') as fd:
        return fd.read().splitlines()


def get_version():
    with open(os.path.join('thoth', 'package_extract', '__init__.py')) as f:
        content = f.readlines()

    for line in content:
        if line.startswith('__version__ ='):
            # dirty, remove trailing and leading chars
            return line.split(' = ')[1][1:-2]
    raise ValueError("No version identifier found")


VERSION = get_version()

setup(
    name='thoth-package-extract',
    version=VERSION,
    entry_points={
        'console_scripts': ['thoth-package-extract=thoth.package_extract.cli:cli']
    },
    packages=[
        'thoth.package_extract',
        'thoth.package_extract.handlers',
    ],
    package_data={
        'thoth.package_extract': [os.path.join('bin', 'skopeo')]
    },
    zip_safe=False,
    install_requires=get_requirements(),
    author='Fridolin Pokorny',
    author_email='fridolin@redhat.com',
    maintainer='Fridolin Pokorny',
    maintainer_email='fridolin@redhat.com',
    description='Tool and library for extracting packages from a docker build log',
    long_description=Path('README.rst').read_text(),
    url='https://github.com/thoth-station/package-extract',
    license='GPLv3+',
    keywords='docker image openshift tool library',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License:: OSI Approved:: GNU General Public License v3 or later(GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"
    ],
    command_options={
        'build_sphinx': {
            'version': ('setup.py', VERSION),
            'release': ('setup.py', VERSION),
        }
    }
)
