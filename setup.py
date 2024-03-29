# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import find_packages
from setuptools import setup
import os.path


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='gocept.gtimelog',
    version='3.0.dev0',
    license='ZPL 2.1',
    description='gocept fork of gtimelog.',
    long_description=read('README.rst'),
    url='https://github.com/gocept/gocept.gtimelog',
    author='gocept gmbh & co. kg',
    author_email='mail@gocept.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['gocept'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Office/Business',
    ],
    python_requires='>=3.7',

    include_package_data=True,
    install_requires=[
        'beautifulSoup4',
        'gocept.collmex>=1.2',
        'pyactiveresource>=2.1',
        'setuptools',
        'soupsieve < 2',  # PY2
        'transaction',
        'zope.cachedescriptors',
        'pync'
    ],
    extras_require={
        'test': [
            'zope.testing',
            'mock',
            'funcsigs'
        ]
    },
    zip_safe=False,
    entry_points="""
        [console_scripts]
        gtl-upload = gocept.gtimelog.cli:main
        gtl-progress = gocept.gtimelog.progress:main
        gtl-log = gocept.gtimelog.log:log
        gtl-updatetasks = gocept.gtimelog.log:download
    """)
