# -*- coding: utf-8 -*-
# (c) 2012, ENDOH takanao

from setuptools import setup, find_packages, Command
import os

VERSION = "1.2.2"
KEYWORDS = 'google reader client gae appengine'
DESCRIPTION = "A Google Reader API client that is optimized for Google App Engine"
LONG_DESCRIPTION = open("README.txt").read()
CLASSIFIERS = [
    "Programming Language :: Python",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Development Status :: 4 - Beta",
    ]

setup(name = 'gaereader',
      version = VERSION,
      description = DESCRIPTION,
      long_description = LONG_DESCRIPTION,
      classifiers = CLASSIFIERS,
      keywords = KEYWORDS,
      license='BSD',
      author='ENDOH takanao',
      author_email='djmchl@gmail.com',
      url='https://github.com/MiCHiLU/gaereader',
      packages=find_packages('gaereader', exclude=['sample', 'tests']),
      include_package_data = True,
      zip_safe = True,
      install_requires=[
        'lxml',
      ],
)
