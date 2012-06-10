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

    def testFinePartialEmpty(self):
        fsc = FileSystemCleaner('/mnt/storage/MUSIC/MUSIC')
        dirs = fsc.findCorruptDirectories()
        for rls, stats in dirs:
            if stats[0]:
                print("{0} {2}/{3} {1}% Empty".format(rls, int(stats[0]/stats[1]*100.0), *stats))
        #fsc.wipeDirs(dirs)


