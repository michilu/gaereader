# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

from setuptools import setup, find_packages
import os
execfile(os.path.join(os.path.dirname(__file__), "src", "mekk", "greader", "version.py"))

KEYWORDS = 'google reader client'
DESCRIPTION = "Simple wrapper for Google Reader API."
LONG_DESCRIPTION = open("README.txt").read()
CLASSIFIERS = [
    "Programming Language :: Python",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    ]

setup(name = 'mekk.greader',
      version = VERSION,
      description = DESCRIPTION,
      long_description = LONG_DESCRIPTION,
      classifiers = CLASSIFIERS,
      keywords = KEYWORDS,
      license='BSD',
      author='Marcin Kasperski',
      author_email='Marcin.Kasperski@mekk.waw.pl',
      url='http://bitbucket.org/Mekk/mekk.greader',
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['mekk'],
      test_suite = 'nose.collector',
      include_package_data = True,
      package_data = {
        'mekk' : [
            'README.txt',
            'LICENSE.txt',
            'doc/usage.txt',
            ],
        },
      zip_safe = True,
      install_requires=[
        'lxml', 'simplejson',
      ],
      tests_require=[
        'nose',
        ],
)
