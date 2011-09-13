#!/bin/env python
"""
Author: Leigh MacDonald <leigh.macdonald@gmail.com>
"""
from os import remove
import unittest
import msort

class ConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conf = msort.Config('~/.msort.test.conf')

    def testRegex(self):
        self.conf.getRules()

    def testParseRules(self):
        self.assertEqual(len(self.conf.sections()) - len(self.conf.skip),
                         len(self.conf.parseRules()))

    def testInstantiateFailPath(self):
        self.assertRaises(Exception, msort.Config, '/path/doesnt/exist')

    def testGetSafeOk(self):
        self.assertEqual('^\.(incomplete|lock|locked)', self.conf.getSafe('general','lock_pattern'))

    def testGetSafeFail(self):
        self.assertEqual('^\.(incomplete|lock|locked)', self.conf.getSafe('general','FAIL_OPTION', '^\.(incomplete|lock|locked)'))

    def testGetSafeFailSection(self):
        self.assertEqual('^\.(incomplete|lock|locked)', self.conf.getSafe('FAIL_SECTION','FAIL_OPTION', '^\.(incomplete|lock|locked)'))

    def testGetSectionRegex(self):
        tv = self.conf.getSectionRegex('tv')
        xvid = self.conf.getSectionRegex('xvid')
        self.assertEqual(2, len(tv))
        self.assertEqual(1, len(xvid))
        tv.extend(xvid)
        [self.assertEqual(r.__class__.__name__, 'SRE_Pattern') for r in tv]

    def testAddRuleOk(self):
        self.conf.addRule('tv', '/rule/')

    def testGetRuleList(self):
        l = list(self.conf.getRuleList('tv'))
        self.assertListEqual([('rx1', '(?P<name>.+?).S\\d{1,2}E\\d{1,2}'), ('rx2', '(?P<name>.+?).\\d{1,2}X\\d{2}')], l)

    def testGetRuleListFail(self):
        self.assertRaises(ValueError, self.conf.getRuleList, 'INVALID')
        
    def testFilteredSections(self):
        self.assertListEqual(['tv','xvid','dvdr','xxx'], list(self.conf.filteredSections()))

    def testGetNextRxId(self):
        self.assertEqual('rx3', self.conf.getNextRxId('tv'))
        
    @classmethod
    def tearDownClass(cls):
        remove(cls.conf.confPath)