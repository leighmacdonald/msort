import unittest

from msort import filesystem

class FilesystemTest(unittest.TestCase):
    def test_invalid_checker(self):
        self.assertRaises(TypeError, filesystem.DirectoryScanner(None).registerChecker, object())

    def test_skip_raised(self):
        pass

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
