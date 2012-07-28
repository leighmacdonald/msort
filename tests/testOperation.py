from os import makedirs, listdir
from os.path import exists, join, dirname
from shutil import rmtree
import unittest
from msort.operation import MoveOperation, DeleteOperation, BaseOperation, OperationError, MoveContentsOperation

class TestOperations(unittest.TestCase):
    def setUp(self):
        try:
            self.dir_root = join(dirname(__file__), 'test_root')
            self.folder = join(self.dir_root, 'test.folder')
            if exists(self.dir_root):
                rmtree(self.dir_root)
            makedirs(self.folder)
            dirs = ['TV/The.Old.Guys.S01.DVDRip.XviD-BTN',
                    'TV/The.Old.Guys.S01.DVDRip.XviD-BTN/The.Old.Guys.S01E01.DVDRip.XviD-BTN',
                    'TV/The.Old.Guys.S01.DVDRip.XviD-BTN/The.Old.Guys.S01E02.DVDRip.XviD-BTN',
                    'TV/The.Old.Guys.S01.DVDRip.XviD-BTN/The.Old.Guys.S01E03.DVDRip.XviD-BTN',
                    'TV/The.Old.Guys.S01.DVDRip.XviD-BTN/The.Old.Guys.S01E04.DVDRip.XviD-BTN',
                    'TV/The.Old.Guys.S01.DVDRip.XviD-BTN/The.Old.Guys.S01E05.DVDRip.XviD-BTN']
            for i, d in enumerate(dirs):
                dir_path = join(self.dir_root,d)
                makedirs(dir_path)
                if i > 0:
                    with open(join(dir_path, '{0}.avi'.format(i)), 'w') as fp:
                        fp.write('x'*1000)
            self.file = join(self.dir_root, 'test.file.avi')
            with open(self.file, 'w') as fp: fp.write('x'*1000)
        except Exception as err:
            errmsg = err.message
            pass

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
        if exists('another.bs.path'):
            rmtree('another.bs.path')

    def testDeleteFileOperation(self):
        DeleteOperation(self.file)()
        self.assertFalse(exists(self.file))

    def testDeleteDirOperation(self):
        do = DeleteOperation(self.dir_root)
        do()
        self.assertFalse(exists(self.dir_root))

    def testMoveContents(self):
        src = join(self.dir_root,'TV','The.Old.Guys.S01.DVDRip.XviD-BTN')
        dest = join(self.dir_root, 'TV', 'The.Old.Guys')
        op = MoveContentsOperation(src, dest)
        op()
        self.assertFalse(exists(src))
        self.assertEqual(5, len(listdir(dest)))



if __name__ == '__main__': unittest.main()