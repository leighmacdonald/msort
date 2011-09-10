#!/bin/env python
"""
Author: Leigh MacDonald <leigh.macdonald@gmail.com>
"""
from os import mkdir
from os.path import exists
from shutil import rmtree
import unittest
import msort

class TestChangeSet(unittest.TestCase):
    def setUp(self):
        self.dir = 'cs_temp'
        if not exists(self.dir):
            mkdir(self.dir)
        self.cs = msort.ChangeSet(self.dir, self.dir*2)

    def testMove(self):
        self.assertFalse(exists(self.cs.dest))
        self.cs.exec()
        self.assertTrue(exists(self.cs.dest))

    def testStringRepr(self):
        self.assertEqual('mv cs_temp cs_tempcs_temp', '{0}'.format(self.cs))

    def tearDown(self):
        if exists(self.dir):
            rmtree(self.dir)
        if exists(self.dir*2):
            rmtree(self.dir*2)