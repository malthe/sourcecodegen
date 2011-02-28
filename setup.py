__version__ = '0.6.13'

import os
import sys

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

version = sys.version_info[:3]

if version < (2,5):
    test_suite = 'sourcecodegen.tests.py24'
else:
    test_suite = 'sourcecodegen.tests.py25plus'

setup(
    name='sourcecodegen',
    version=__version__,
    description='A Python source-code generator based on the ``compiler.ast`` ' + 
                'abstract syntax tree.',
    long_description="\n\n".join((README, CHANGES)),
    classifiers=[
       "Development Status :: 6 - Mature",
       "Intended Audience :: Developers",
       "Programming Language :: Python",
       "Topic :: Internet :: WWW/HTTP",
       "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
       "Topic :: Internet :: WWW/HTTP :: WSGI",
       "Programming Language :: Python :: 2.4",
       "Programming Language :: Python :: 2.5",
       "Programming Language :: Python :: 2.6",
       "Programming Language :: Python :: 2.7",
      ],
    keywords='python source-code generation ast',
    author="Malthe Borch",
    author_email="mborch@gmail.com",
    url="http://chameleon.repoze.org",
    license='BSD-like (http://repoze.org/license.html)',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    test_suite=test_suite,
    )

