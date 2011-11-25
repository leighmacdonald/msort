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
        subdir_data = join(self.testdir,'data1')
        mkdir(subdir_data)
        open(join(subdir_data, 'data.file'), 'w').write('Hello!')

    def tearDown(self):
        rmtree(self.testdir)
        
    def testFindEmpty(self):
        fsc = FileSystemCleaner(self.testdir)
        dirs = fsc.findEmptyDirectories()
        self.assertEqual(1, len(dirs))