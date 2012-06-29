from os import remove
from os.path import exists
from msort.check import CheckSkip
from msort.check.inuse import InUseCheck

import unittest

class TestInUseScanner(unittest.TestCase):
    def test_openfilescan(self):
        file_path = 'open_file'
        try:
            with open(file_path, 'w') as fp: fp.write('')
        except: pass
        with open(file_path) as openfile:
            scanner = InUseCheck(None)
            self.assertRaises(CheckSkip, scanner, None, file_path)
        if exists(file_path):
            remove(file_path)

    def test_unopenedfile(self):
        file_path = 'open_file'
        try:
            with open(file_path, 'w') as fp: fp.write('')
        except: pass
        scanner = InUseCheck(None)
        self.assertFalse(scanner(None, file_path))
        if exists(file_path):
            remove(file_path)

if __name__ == '__main__': unittest.main()
