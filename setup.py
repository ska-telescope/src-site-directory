#!/usr/bin/env python

import glob

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

data_files = [
    ('etc', glob.glob('etc/*')),
]

setup(
    name='site_directory',
    version='0.1.0',
    description='A utility to keep track of resources',
    url='',
    author='rob barnsley',
    author_email='rob.barnsley@skao.int',
    packages=['site_directory.rest', 'site_directory.common'],
    package_dir={'': 'src'},
    data_files=data_files,
    include_package_data=True,
    install_requires=requirements,
    classifiers=[]
)
