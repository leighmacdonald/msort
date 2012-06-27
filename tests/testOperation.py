from os import makedirs, listdir
from os.path import exists, join, dirname
from shutil import rmtree
import unittest
from msort.operation import MoveOperation, DeleteOperation

class TestOperations(unittest.TestCase):
    def setUp(self):
        try:
            self.dir_root = join(dirname(__file__), 'test_root')
            makedirs(self.dir_root)
            self.folder = join(self.dir_root, 'test.folder')
            makedirs(self.folder)
            self.file = join(self.dir_root, 'test.file.avi')
            with open(self.file, 'w') as fp: fp.write('x'*1000)
        except: pass

    def tearDown(self):
        try: rmtree(self.dir_root)
        except: pass

    def testMoveOperation(self):
        MoveOperation(join(self.dir_root, 'test.file.avi'), self.folder)()
        self.assertTrue('test.file.avi' in listdir(self.folder))

    def testDeleteOperation(self):
        DeleteOperation(self.file)()
        self.assertFalse(exists(self.file))

if __name__ == '__main__':
    unittest.main()