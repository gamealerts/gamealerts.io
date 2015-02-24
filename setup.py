#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import gamealerts.io
version = gamealerts.io.__version__

setup(
    name='gamealerts.io',
    version=version,
    author="Jay",
    author_email='jay@gamealerts.io',
    packages=[
        'gamealerts.io',
    ],
    include_package_data=True,
    install_requires=[
        'Django>=1.7.4',
    ],
    zip_safe=False,
    scripts=['gamealerts.io/manage.py'],
)
