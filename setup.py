# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Setup for gocept.gtimelog package"""

import sys
import os.path

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = 'gocept.gtimelog'

setup(
    name=name,
    version = '0.1',
    license='ZPL 2.1',
    description='gocept fork of gtimelog.',
    long_description = (read('README.txt')),
    author='gocept',
    author_email='sw@gocept.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['gocept',],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'gocept.collmex',
    ],
    zip_safe=False,
    )
