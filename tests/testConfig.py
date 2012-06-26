#!/bin/env python
"""
Author: Leigh MacDonald <leigh.macdonald@gmail.com>
"""
from os import remove
from os.path import join, dirname, exists
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from msort.conf import Config

class ConfigTest(unittest.TestCase):

    def setUp(self):
        self.config_path = join(dirname(__file__), 'msort_test.conf')
        self.conf = Config(config_path=self.config_path)

    def testRegex(self):
        self.conf.getRules()

    def testParseRules(self):
        self.assertEqual(len(self.conf.sections()) - len(self.conf.skip),
                         len(self.conf.parseRules()))

    def testGetSafeOk(self):
        self.assertEqual('^\.(incomplete|lock|locked)', self.conf.getSafe('general','lock_pattern'))

    def testGetSafeFail(self):
        self.assertEqual('^\.(incomplete|lock|locked)', self.conf.getSafe('general','FAIL_OPTION', '^\.(incomplete|lock|locked)'))

    def testGetSafeFailSection(self):
        self.assertEqual('^\.(incomplete|lock|locked)', self.conf.getSafe('FAIL_SECTION','FAIL_OPTION', '^\.(incomplete|lock|locked)'))

    def testGetSectionRegex(self):
        tv = self.conf.getSectionRegex('TV')
        xvid = self.conf.getSectionRegex('XVID')
        self.assertEqual(2, len(tv))
        self.assertEqual(1, len(xvid))
        tv.extend(xvid)
        [self.assertEqual(type(r).__name__, 'SRE_Pattern') for r in tv]

    def testAddRuleOk(self):
        self.conf.addRule('TV', '/rule/')

    def testGetRuleList(self):
        l = list(self.conf.getRuleList('TV'))
        self.assertEqual([('rx1', '(?P<name>.+?).S\\d{1,2}E\\d{1,2}'), ('rx2', '(?P<name>.+?).\\d{1,2}X\\d{2}')], l)

    def testGetRuleListFail(self):
        self.assertRaises(ValueError, self.conf.getRuleList, 'INVALID')
        
    def testFilteredSections(self):
        self.assertEqual(['TV', 'DVDR', 'XVID'], list(self.conf.filteredSections()))

    def testGetNextRxId(self):
        self.assertEqual('rx3', self.conf.getNextRxId('TV'))
