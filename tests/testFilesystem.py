import unittest
from os.path import join, dirname, exists
from os import makedirs
from shutil import rmtree
from msort import filesystem
from msort.check import CheckError, CheckSkip
from msort.check.empty import EmptyCheck
from msort.check.inuse import InUseCheck



class FilesystemTest(unittest.TestCase):
    def setUp(self):
        self.dir_root = join(dirname(__file__), 'test_root')
        self.folder = join(self.dir_root, 'test.folder')
        self.file = join(self.dir_root, 'test.file.avi')
        try:
            makedirs(self.folder)
            with open(self.file, 'w') as fp: fp.write('x'*1000)
        except: pass

    def tearDown(self):
        if exists(self.dir_root):
            rmtree(self.dir_root)

    def test_invalid_checker(self):
        self.assertRaises(TypeError, filesystem.DirectoryScanner(None).registerChecker, object())

    def test_skip_raised(self):
        from init_test_config import conf
        section = 'TEST'
        conf.conf.add_section(section)
        conf.conf.set(section, 'source', self.dir_root)
        ds = filesystem.DirectoryScanner(conf)
        ds.registerChecker(InUseCheck(conf))
        ds.registerChecker(EmptyCheck(conf))
        empty_file = join(self.dir_root, 'empty_file')
        open(empty_file, 'w').write('')
        with open(empty_file) as fp:
            res = ds.find(section)
            self.assertEqual(1, len(res))

    def test_error_raised(self):
        pass

    def test_dir_size(self):
        size = filesystem.dir_size('./')
        self.assertTrue(size > 0)

    def test_disk_usage(self):
        usage = filesystem.disk_usage('/')
        self.assertTrue(usage.total == usage.used + usage.free, usage.total)

    def test_fmt_size(self):
        self.assertEqual('1.0b', filesystem.fmt_size(1))
        self.assertEqual('1.0KB', filesystem.fmt_size(1024))
        self.assertEqual('1.0MB', filesystem.fmt_size(1024**2))
        self.assertEqual('1.0GB', filesystem.fmt_size(1024**3))
        self.assertEqual('1.0TB', filesystem.fmt_size(1024**4))
        self.assertEqual('1024.0TB', filesystem.fmt_size(1024**5))

if __name__ == '__main__':
    unittest.main()
