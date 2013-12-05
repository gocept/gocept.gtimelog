# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages
import os.path


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='gocept.gtimelog',
    version='0.8.5.dev0',
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
        'BeautifulSoup',
        'gocept.collmex>=1.2',
        'jira-python',
        'pyactiveresource==1.2dev-r77',
        'setuptools',
        'transaction',
        'zope.cachedescriptors',
    ],
    zip_safe=False,
    entry_points="""
        [console_scripts]
        gtimelog = gocept.gtimelog.gtimelog:main
        gtl-upload = gocept.gtimelog.cli:main
        gtl-progress = gocept.gtimelog.progress:main
        gtl-log = gocept.gtimelog.log:log
        gtl-updatetasks = gocept.gtimelog.log:download
    """)
