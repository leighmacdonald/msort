#!/bin/env python
"""
Author: Leigh MacDonald <leigh@cudd.li>
"""


from os import mkdir
from os.path import join, exists
from shutil import rmtree
from unittest import TestCase

from msort.cleaner import FileSystemCleaner

class TestCleaner(TestCase):

    def setUp(self):
        self.testdir = 'test'
        if exists(self.testdir):
            self.tearDown()
        mkdir(self.testdir)
        subdir = join(self.testdir,'empty1')
        mkdir(subdir)
        open(join(subdir, 'test.file'), 'w').write("")

    def tearDown(self):
        rmtree(self.testdir)
        
    def testFindEmpty(self):
        fsc = FileSystemCleaner(self.testdir)
        fsc.findEmptyDirectories()