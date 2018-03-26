#!/usr/bin/python3

import os
from setuptools import setup


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


def get_long_description():
    with open('README.rst', 'r') as f:
        return f.read()


setup(
    name='thoth-package-extract',
    version=get_version(),
    entry_points={
        'console_scripts': ['thoth-package-extract=thoth.package_extract.cli:cli']
    },
    packages=[
        'thoth.package_extract',
        'thoth.package_extract.handlers',
    ],
    zip_safe=False,
    install_requires=get_requirements(),
    author='Fridolin Pokorny',
    author_email='fridolin@redhat.com',
    maintainer='Fridolin Pokorny',
    maintainer_email='fridolin@redhat.com',
    description='Tool and library for extracting packages from a docker build log',
    long_description=get_long_description(),
    url='https://github.com/fridex/thoth-package-extract',
    license='ASL v2.0',
    keywords='docker image openshift tool library',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"
    ]
)
