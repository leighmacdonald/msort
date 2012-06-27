from os import makedirs
from os.path import exists, join, dirname
from shutil import rmtree
from logging import basicConfig, DEBUG
import unittest

from init_test_config import conf

from msort.filesystem import DirectoryScanner
from msort.check import DummyCheck
from msort.check.empty import EmptyCheck
from msort.check.release import ReleaseCheck

basicConfig(level=DEBUG)

class TestScanner(unittest.TestCase):
    def setUp(self):
        dirs = [
            'TestFolder',
            'TV/Entourage.S08E06.HDTV.Custom.HebSub.XviD-Extinct',
            'TV/Bridezillas.S08E12.DSR.XviD-OMiCRON',
            'XVID/Not.Another.Not.Another.Movie.2011.HDRip.XVID.AC3.HQ.Hive-CM8',
            'TV/History.of.ECW.1997.11.04.PDTV.XviD-W4F',
            'TV/file.avi',
            'TV/NOVA.S39E16.480p.HDTV.x264-mSD.mkv',
            'TV/RegularShow.s03e16.ButtDial.mp4',
            'TV/Crave.S01E01.HDTV.XviD-SYS',
            'X264/The.Terrorist.2010.720p.BluRay.x264-aAF',
            'XVID/TrollHunter.2010.LiMiTED.BDRip.XviD-NODLABS',
            'XVID/Tyler.Perrys.Laugh.To.Keep.From.Crying.2009.DVDRip.XviD-IGUANA',
            'DVDR/Blah.Blah.XXX.NTSC.DVDR-EvilAngel',
            'DVDR/Feed.The.Fish.LIMITED.R2.PAL.DVDR-TARGET',
        ]
        self.sections = ('TV', 'XVID', 'DVDR')
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
            makedirs(join(self.root_path, 'TV/Top.Gear.17x06.HDTV.XviD-FoV'))
        except: pass
        try:
            # Empty file check
            with open(join(self.root_path, 'TV/empty.file.avi'), 'w') as fp: fp.write('')
        except: pass


    def tearDown(self):
        rmtree(self.root_path)

    def testReleaseCheck(self):
        scanner = DirectoryScanner(conf)
        scanner.registerChecker(ReleaseCheck(conf))
        changes = {}
        for section in self.sections:
            changes[section] = scanner.find(section)
        self.assertEquals(len(changes['DVDR']), 2)
        self.assertEquals(len(changes['XVID']), 2)
        self.assertEquals(len(changes['TV']), 6)

    def testEmptyCheck(self):
        scanner = DirectoryScanner(conf)
        scanner.registerChecker(EmptyCheck(conf))
        changes = []
        for section in self.sections:
            changes.extend(scanner.find(section))
        self.assertEquals(len(changes), 2)

    def testDupeChecks(self):
        scanner = DirectoryScanner(conf)
        scanner.registerChecker(DummyCheck(conf))
        scanner.registerChecker(DummyCheck(conf))
        self.assertTrue(len(scanner._checks) == 2)