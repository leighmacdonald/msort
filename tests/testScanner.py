from os import makedirs
from os.path import exists, join, dirname
from shutil import rmtree
from logging import basicConfig, DEBUG
import unittest

from msort.filesystem import DirectoryScanner
from msort.check import DummyCheck
from msort.check.empty import EmptyCheck
from msort.check.release import ReleaseCheck

basicConfig(level=DEBUG)

class TestChecker(unittest.TestCase):
    def setUp(self):
        dirs = [
            'TestFolder',
            'Entourage.S08E06.HDTV.Custom.HebSub.XviD-Extinct',
            'Bridezillas.S08E12.DSR.XviD-OMiCRON',
            'Not.Another.Not.Another.Movie.2011.HDRip.XVID.AC3.HQ.Hive-CM8',
            'History.of.ECW.1997.11.04.PDTV.XviD-W4F',
            'file.avi',
            'Crave.S01E01.HDTV.XviD-SYS',
            'The.Terrorist.2010.720p.BluRay.x264-aAF',
            'TrollHunter.2010.LiMiTED.BDRip.XviD-NODLABS',
            'Tyler.Perrys.Laugh.To.Keep.From.Crying.2009.DVDRip.XviD-IGUANA',
            'Deep.Anal.Drilling.3.XXX.DVDRip.XviD-Jiggly',
            'Blah.Blah.XXX.NTSC.DVDR-EvilAngel',
            'Feed.The.Fish.LIMITED.R2.PAL.DVDR-TARGET',
        ]
        write_data = 'x'*10000000
        self.root_path = join(dirname(__file__), 'test_root')
        if not exists(self.root_path):
            makedirs(self.root_path)
        for d in [join(self.root_path, p) for p in dirs]:
            try:
                if d.endswith('.avi'):
                    # Create files
                    with open(d, 'w') as fp:
                        fp.write(write_data)
                else:
                    # Create directories with a file inside
                    makedirs(d)
                    with open(join(d, 'blah.rar'), 'w') as fp:
                        fp.write(write_data)
            except Exception as err:
                pass
        try:
            # Empty dir check
            makedirs(join(self.root_path, 'Top.Gear.17x06.HDTV.XviD-FoV'))
        except: pass
        try:
            # Empty file check
            with open(join(self.root_path, 'empty.file.avi'), 'w') as fp: fp.write('')
        except: pass


    def tearDown(self):
        rmtree(self.root_path)

    def testReleaseCheck(self):
        scanner = DirectoryScanner()
        scanner.addChecker(ReleaseCheck())
        changes = scanner.find(self.root_path)
        self.assertEquals(len(changes), 2)

    def testEmptyCheck(self):
        scanner = DirectoryScanner()
        scanner.addChecker(EmptyCheck())
        changes = scanner.find(self.root_path)
        self.assertEquals(len(changes), 2)

    def testDupeChecks(self):
        scanner = DirectoryScanner()
        scanner.addChecker(DummyCheck())
        scanner.addChecker(DummyCheck())
        self.assertTrue(len(scanner._checks) == 2)