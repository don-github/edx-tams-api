#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='edx-tams-api',
    version='v0.0.1',
    description='TAMS REST API for Open edX',
    author='kencung',
    url='https://github.com/kencung/edx-tams-api',
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
