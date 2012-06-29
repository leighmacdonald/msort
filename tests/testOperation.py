from os import makedirs, listdir
from os.path import exists, join, dirname
from shutil import rmtree
import unittest
from msort.operation import MoveOperation, DeleteOperation, BaseOperation, OperationError

class TestOperations(unittest.TestCase):
    def setUp(self):
        try:
            self.dir_root = join(dirname(__file__), 'test_root')
            self.folder = join(self.dir_root, 'test.folder')
            makedirs(self.folder)
            self.file = join(self.dir_root, 'test.file.avi')
            with open(self.file, 'w') as fp: fp.write('x'*1000)
        except: pass

    def testInvalidImplementation(self):
        self.assertRaises(NotImplementedError, BaseOperation())

    def testStringRepr(self):
        self.assertEqual('BaseOperation', str(BaseOperation()))

    def tearDown(self):
        try: rmtree(self.dir_root)
        except: pass

    def testMoveOperation(self):
        MoveOperation(join(self.dir_root, 'test.file.avi'), self.folder)()
        self.assertTrue('test.file.avi' in listdir(self.folder))

    def testMoveInvalid(self):
        op = MoveOperation('bs.path', 'another.bs.path')
        self.assertRaises(OperationError, op)

    def testDeleteFileOperation(self):
        DeleteOperation(self.file)()
        self.assertFalse(exists(self.file))

    def testDeleteDirOperation(self):
        do = DeleteOperation(self.dir_root)
        do()
        self.assertFalse(exists(self.dir_root))


if __name__ == '__main__': unittest.main()