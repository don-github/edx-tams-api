#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='edx-accounts-api',
    version='v0.0.2',
    description='Accounts REST Api for Open edX',
    author='kencung',
    url='https://github.com/kencung/edx-accounts-api',
    license='AGPL',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    packages=find_packages(exclude=['tests', '*.tests'])
)
