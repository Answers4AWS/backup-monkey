#!/usr/bin/env python
# Copyright 2013 Answers for AWS LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
distutils/setuptools install script for Backup Monkey
"""

import sys, os
major, minor = sys.version_info[0:2]
if major != 2 or minor < 7:
    print 'Backup Monkey requires Python 2.7.x'
    sys.exit(1)

from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup

sys.path.insert(0, os.path.abspath('lib'))
import backup_monkey

requires = [
    'boto>=2.7'
]

entry_points = {
    'console_scripts': [
        'backup-monkey = backup_monkey.cli:run',
    ]
}

packages = [
    'backup_monkey'
]

setup(
    name='backup_monkey',
    version=backup_monkey.__version__,
    description='A service that makes sure you have snapshots of all your EBS volumes',
    long_description=open('README.rst').read(),
    author=backup_monkey.__author__,
    author_email='info@answersforaws.com',
    url='https://github.com/Answers4AWS/backup-monkey',
    packages=packages,
    package_dir={'backup_monkey': 'lib/backup_monkey'},
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points=entry_points,
    license=open("LICENSE.txt").read(),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Installation/Setup',
        'Topic :: Utilities',
    )
)
