#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from setuptools import (
    find_packages,
    setup,
)

setup_dir = os.path.dirname(__file__)
version_path = os.path.join(setup_dir, 'precognise/version.py')

with open(version_path) as f:
    version = re.match('.*= *\"(.*)"', f.read()).group(1)


with open('requirements.txt') as f:
    requirements = [line for line in f.read().split('\n') if line]

readme = open('README.md').read()
history = open('CHANGES').read().replace('.. :changelog:', '')

setup(
    name='precognise',
    version=version,
    description='Basic CLI construction',
    long_description=readme + '\n\n' + history,
    author='Osper Ltd',
    author_email='dev@osper.com',
    url='https://github.com/osper-os/precognise',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
)
