from os import makedirs, link, unlink, utime
from os.path import exists, join, dirname
from shutil import rmtree
import unittest

from init_test_config import conf

from msort.filesystem import DirectoryScanner
from msort.check import DummyCheck
from msort.check.empty import EmptyCheck
from msort.check.release import ReleaseCheck
from msort.check.prune import Pruner
from msort.operation import filterType, MoveContentsOperation

class TestScanner(unittest.TestCase):
    def setUp(self):
        dirs = [
            'TestFolder',
            'TV/Entourage.S08E06.HDTV.Custom.HebSub.XviD-Extinct',
            'TV/Bridezillas.S08E12.DSR.XviD-OMiCRON',
            'SRC_XVID/Not.Another.Not.Another.Movie.2011.HDRip.XVID.AC3.HQ.Hive-CM8',
            'TV/History.of.ECW/History.of.ECW.1997.11.04.HDTV.XviD-W4F',
            'TV/file.avi',
            'TV/NOVA.S39E16.480p.HDTV.x264-mSD.mkv',
            'TV/RegularShow.s03e16.ButtDial.mp4',
            'TV/Crave.S01E01.HDTV.XviD-SYS',
            'SRC_X264/The.Terrorist.2010.720p.BluRay.x264-aAF',
            'SRC_XVID/TrollHunter.2010.LiMiTED.BDRip.XviD-NODLABS',
            'SRC_XVID/Tyler.Perrys.Laugh.To.Keep.From.Crying.2009.DVDRip.XviD-IGUANA',
            'SRC_DVDR/Blah.Blah.XXX.NTSC.DVDR-EvilAngel',
            'SRC_DVDR/Feed.The.Fish.LIMITED.R2.PAL.DVDR-TARGET',
            'TV/Jonathan Creek - Series 1',
            'TV/Kingdom.S01.DVDRip.XviD-BTN',
            'TV/Will.And.Grace.S01.DVDRip.XviD-FOV',
            'TV/Will.And.Grace.S18.DVDRip.XviD-SAiNTS',
            'TV/The Twilight Zone Season 5',
            'TV/The Thick Of It S01',
            'TV/The Thick Of It S02',
            'TV/The.Thick.Of.It.Season.3.Xvid-BTN',
            'TV/The.Thick.Of.It.Season.3.Xvid-BTN/The.Thick.Of.It.S01E01.DVDRip.XviD-BTN',
            'TV/The.Thick.Of.It.Season.3.Xvid-BTN/The.Thick.Of.It.S01E02.DVDRip.XviD-BTN',
            'TV/The.Old.Guys.S01.DVDRip.XviD-BTN',
            'TV/The.Old.Guys.S01.DVDRip.XviD-BTN/The.Old.Guys.S01E01.DVDRip.XviD-BTN',
            'TV/The.Old.Guys.S01.DVDRip.XviD-BTN/The.Old.Guys.S01E02.DVDRip.XviD-BTN',
            'TV/The.Old.Guys.S01.DVDRip.XviD-BTN/The.Old.Guys.S01E03.DVDRip.XviD-BTN',
            'TV/The.Old.Guys.S01.DVDRip.XviD-BTN/The.Old.Guys.S01E04.DVDRip.XviD-BTN',
            'TV/The.Old.Guys.S01.DVDRip.XviD-BTN/The.Old.Guys.S01E05.DVDRip.XviD-BTN',
            'TV/The Life and Times of Tim - Season 1 DVDRip',
            'TV/The.Life.and.Times.of.Tim.S03.HDTV.XviD-BTN',
            'TV/The.Life.and.Times.of.Tim.S02.DVDRip.XviD-REWARD',
            'TV/La Femme Nikita Season 1',
            'TV/Jeeves.and.Wooster.S01.DVDRip.DivX',
            'TV/Japanorama-Season 01',
            'TV/Japanorama-S03',
            'TV/Inside.The.Human.Body.S01.DVDRip.XviD-BTN',
            'TV/Im.Alan.Partridge.S01.576p.DVDRip.DD2.0.x264-SDB',
            'TV/How.I.Met.Your.Mother.S01-03.DVDRip.XviD',
            'TV/Hatfields.and.McCoys.2012.Part.1.REPACK.720p.HDTV.x264-2HD',
            'TV/Hatfields.and.McCoys.2012.Part.2.720p.HDTV.x264-2HD',
            'TV/Wild India.pt1.Elephant Kingdom.thebox.hannibal.mkv',
            'TV/Wild India.pt2.Tiger Jungles.thebox.hannibal.mkv',
            'TV/Deadliest Warrior S01',
            'TV/Comedy Central Presents - Season 9',
            'TV/Comedy.Central.Presents.S04.PDTV.mp3.XviD-BTN'
        ]
        self.sections = ('TV', 'XVID', 'DVDR')
        write_data = 'x'*1000
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
        utime(join(self.root_path, 'TV/History.of.ECW/History.of.ECW.1997.11.04.HDTV.XviD-W4F'), (0,0))
        try:
            link(join(self.root_path, 'TV/file.avi'), join(self.root_path, 'TV/file-link.avi'))
        except : pass
        try:
            # Empty dir check
            makedirs(join(self.root_path, 'TV/Top.Gear.17x06.HDTV.XviD-FoV'))
        except: pass
        try:
            # Empty file check
            with open(join(self.root_path, 'TV/empty.file.avi'), 'w') as fp: fp.write('')
        except: pass


    def tearDown(self):
        try:
            unlink('TV/file-link.avi')
        except : pass
        rmtree(self.root_path)

    def testReleaseCheck(self):
        conf.set('TV', 'sort_seasons', 'false')
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

    def testPruneCheck(self):
        scanner = DirectoryScanner(conf)
        scanner.registerChecker(Pruner(conf))
        changes = []
        for section in self.sections:
            changes.extend(scanner.find(section))
        self.assertEquals(len(changes), 1)

    def testSeasonDetection(self):
        conf.set('TV', 'sort_seasons', 'true')
        scanner = DirectoryScanner(conf)
        scanner.registerChecker(ReleaseCheck(conf))
        changes = {}
        for section in self.sections:
            changes[section] = scanner.find(section)
        self.assertEqual(22, len(list(filterType(changes['TV'], MoveContentsOperation))))


if __name__ == '__main__': unittest.main()