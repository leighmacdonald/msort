import unittest
from msort import system

class SystemTest(unittest.TestCase):
    def test_call_output(self):
        res = system.call_output(['echo', 'Hello!'])
        self.assertEqual('Hello!', res)