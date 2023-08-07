#!/usr/bin/env python

import glob

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

data_files = [
    ('etc', glob.glob('etc/*')),
]
scripts = glob.glob('bin/*')

setup(
    name='ska_src_site_capabilities_api',
    version='0.1.0',
    description='An API to keep track of site information and capabilities for SRCNet.',
    url='',
    author='rob barnsley',
    author_email='rob.barnsley@skao.int',
    packages=['ska_src_site_capabilities_api.db', 'ska_src_site_capabilities_api.rest', 'ska_src_site_capabilities_api.common', 'ska_src_site_capabilities_api.client'],
    package_dir={'': 'src'},
    data_files=data_files,
    scripts=scripts,
    include_package_data=True,
    install_requires=requirements,
    classifiers=[]
)
