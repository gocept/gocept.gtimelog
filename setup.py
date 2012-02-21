# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages
import os.path


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='gocept.gtimelog',
    version='0.6.1.dev0',
    license='ZPL 2.1',
    description='gocept fork of gtimelog.',
    long_description=read('README.txt'),
    author='gocept gmbh & co. kg',
    author_email='mail@gocept.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['gocept'],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'BeautifulSoup',
        'lxml',
        'gocept.collmex>=1.2',
        'pyactiveresource==1.2dev-r77',
        'transaction',
        'zope.cachedescriptors',
    ],
    zip_safe=False,
    entry_points="""
        [console_scripts]
        gtimelog = gocept.gtimelog.gtimelog:main
        gtimelog-cli = gocept.gtimelog.cli:main
    """)
