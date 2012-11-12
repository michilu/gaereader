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

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

class PyTestWithCov(PyTest):
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py', '--cov-report=html', '--cov=.', '--pdb'])
        raise SystemExit(errno)

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
      cmdclass = {
        'test': PyTest,
        'cov': PyTestWithCov,
      },
)
