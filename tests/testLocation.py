#!/bin/env python
"""
Author: Leigh MacDonald <leigh.macdonald@gmail.com>
"""
from os import mkdir
from os.path import exists
from shutil import rmtree
import unittest
import msort

class TestLocation(unittest.TestCase):
    def setUp(self):
        self.dir = 'testdir'

    def testValidOk(self):
        mkdir(self.dir)
        loc = msort.Location(self.dir)
        self.assertEqual(loc.path, self.dir)
        rmtree(self.dir)

    def testValidFail(self):
        self.assertRaises(IOError, msort.Location, self.dir + '_')

    def testPath(self):
        self.assertEqual(msort.Location(self.dir, validate=False).path, self.dir)

    def testExistOk(self):
        mkdir(self.dir)
        self.assertTrue(msort.Location(self.dir, validate=False).exists())
        rmtree(self.dir)

    def testExistFail(self):
        self.assertFalse(msort.Location(self.dir, validate=False).exists())

    def testStrRepr(self):
        mkdir(self.dir)
        self.assertTrue(exists('{0}'.format(msort.Location(self.dir))))
        rmtree(self.dir)