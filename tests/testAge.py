from os import remove, utime
from os.path import exists
from msort.filesystem import Path
from msort.conf import Config
from msort.check import CheckSkip
from msort.check.age import AgeCheck

import unittest

class TestAgeScanner(unittest.TestCase):
    def setUp(self):
        self.config = Config('msort_test.conf')
        self.config.set('minimum_age', 'enabled', 'true')

    def test_open_new(self):
        file_path = Path('open_file')
        try:
            with open(file_path, 'w') as fp: fp.write('')
        except: pass
        scanner = AgeCheck(self.config)
        self.assertRaises(CheckSkip, scanner, None, file_path)
        if exists(file_path):
            remove(file_path)

    def test_open_old(self):
        file_path = Path('open_file')
        try:
            with open(file_path, 'w') as fp: fp.write('')
        except: pass
        utime(file_path, (1000,1000))
        scanner = AgeCheck(self.config)
        scanner(None, file_path)
        if exists(file_path):
            remove(file_path)

if __name__ == '__main__':
    unittest.main()
