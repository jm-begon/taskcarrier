# -*- coding: utf-8 -*-
"""
setup script
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"

from distutils.core import setup

import taskcarrier

NAME = "taskcarrier"
VERSION = taskcarrier.__version__
AUTHOR = "Jean-Michel Begon"
AUTHOR_EMAIL = "jm.begon@gmail.com"
URL = 'https://github.com/jm-begon/taskcarrier/'
DESCRIPTION = 'Tools for monitoring progresses'
with open('README.md') as f:
    LONG_DESCRIPTION = f.read()
CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Education',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Topic :: System :: Logging',
    'Topic :: Utilities',
    'Topic :: Software Development :: Libraries',
]



if __name__ == '__main__':
    setup(name=NAME,
          version=VERSION,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          url=URL,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          license='BSD',
          classifiers=CLASSIFIERS,
          platforms='any',
          packages=['taskcarrier', 'taskcarrier.test'])

