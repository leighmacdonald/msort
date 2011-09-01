#!/bin/env python
"""
Author: Leigh MacDonald <leigh.macdonald@gmail.com>
"""

from distutils.core import setup

setup(
    name='msort',
    version='1.0',
    description='utility for sorting scene releases into grouped subfolders',
    author='Leigh MacDonald',
    author_email='leigh@cudd.li',
    url='https://msort.cudd.li/',
    packages=['msort'],
    scripts=['scripts/sort.py'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Programming Language :: Python :: 3'
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Utilities'
    ]
)