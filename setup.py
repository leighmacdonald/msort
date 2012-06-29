#!/bin/env python3
"""
Author: Leigh MacDonald <leigh.macdonald@gmail.com>
"""
from unittest import TextTestRunner, TestLoader
from glob import glob
from os.path import splitext, basename, join
from os import getcwd
try:
    from os.path import walk
except ImportError:
    from os import walk

from distutils.core import setup, Command

class TestCommand(Command):
    user_options = [ ]

    def initialize_options(self):
        self._dir = getcwd()

    def finalize_options(self):
        pass

    def run(self):
        """
        Finds all the tests modules in tests/, and runs them.
        """
        testfiles = [ ]
        for t in filter(lambda f: not f.endswith('__init__.py'), glob(join(self._dir, 'tests', '*.py'))):
            testfiles.append('.'.join(['tests', splitext(basename(t))[0]]))
        tests = TestLoader().loadTestsFromNames(testfiles)
        t = TextTestRunner(verbosity = 1)
        t.run(tests)
setup(
    name='msort',
    version='2.0',
    description='Utility for sorting scene releases into grouped subfolders',
    author='Leigh MacDonald',
    author_email='leigh@cudd.li',
    url='https://msort.cudd.li/',
    packages=['msort', 'msort.check'],
    scripts=['mediasort.py'],
    cmdclass = { 'test': TestCommand },
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