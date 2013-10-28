#! /usr/bin/env python

from distutils.core import setup

setup(name           = 'rotator',
    version          = '0.1.0',
    description      = 'Piped log rotation utility',
    url              = 'http://github.com/dlecocq/rotator',
    author           = 'Dan Lecocq',
    author_email     = 'dan@moz.com',
    scripts          = ['bin/rotator'],
    py_modules       = ['rotator'],
    classifiers      = [
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP'
    ]
)
