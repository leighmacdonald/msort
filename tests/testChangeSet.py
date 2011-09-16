#!/bin/env python
"""
Author: Leigh MacDonald <leigh.macdonald@gmail.com>
"""
from os import mkdir
from os.path import exists
from shutil import rmtree
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import msort

class TestChangeSet(unittest.TestCase):
    def setUp(self):
        self.dir = 'cs_temp'
        if not exists(self.dir):
            mkdir(self.dir)
        self.cs = msort.ChangeSet(self.dir, '{0}{0}'.format(self.dir))

    def testMove(self):
        self.assertFalse(exists(self.cs.dest))
        self.cs(commit=True)
        self.assertTrue(exists(self.cs.dest), "wtf")

    def testStringRepr(self):
        self.assertEqual('move cs_temp cs_tempcs_temp', '{0}'.format(self.cs))

    def tearDown(self):
        if exists(self.dir):
            rmtree(self.dir)
        if exists(self.dir*2):
            rmtree(self.dir*2)