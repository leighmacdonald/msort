from os import mkdir, remove
from os.path import exists, join
from shutil import rmtree
import unittest
import msort

class TestMSorter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dirs = [
            'TestFolder',
            'Entourage.S08E06.HDTV.Custom.HebSub.XviD-Extinct',
            'Bridezillas.S08E12.DSR.XviD-OMiCRON',
            'Not.Another.Not.Another.Movie.2011.HDRip.XVID.AC3.HQ.Hive-CM8',
            'History.of.ECW.1997.11.04.PDTV.XviD-W4F',
            'Crave.S01E01.HDTV.XviD-SYS',
            'The.Terrorist.2010.720p.BluRay.x264-aAF',
            'TrollHunter.2010.LiMiTED.BDRip.XviD-NODLABS',
            'Tyler.Perrys.Laugh.To.Keep.From.Crying.2009.DVDRip.XviD-IGUANA',
            'Deep.Anal.Drilling.3.XXX.DVDRip.XviD-Jiggly',
            'Anal.Ecstasy.XXX.NTSC.DVDR-EvilAngel',
            'Feed.The.Fish.LIMITED.R2.PAL.DVDR-TARGET'
        ]
        cls._dir = 'testdir'
        if not exists(cls._dir):
            mkdir('testdir')
        for d in dirs:
            try:
                mkdir(join(cls._dir, d))
            except Exception as err:
                pass
        cls._location = msort.Location(cls._dir)
        cls._conf = msort.Config('~/.msort.test.conf')
        cls._conf.set('general', 'basepath', cls._dir)
        cls._msort = msort.MSorter(cls._location, config=cls._conf)

    @classmethod
    def tearDownClass(cls):
        rmtree(cls._dir)
        remove(cls._conf.confPath)
        
    def testBasePath(self):
        self._msort.setBasePath(msort.Location(self._dir))
        self.assertEqual(self._location.path, self._dir)
        
    def testGenPath(self):
        self.assertEqual(self._msort._genPath('Test.Path'), join('testdir', 'Test.Path'))
        
    def testTV1(self):
        mtype, dest = self._msort.findParentDir('Entourage.S08E06.HDTV.Custom.HebSub.XviD-Extinct')
        self.assertEqual(dest, join(self._dir, 'TV', 'Entourage'))
        self.assertEqual(mtype, 'tv')
        
    def testTV2(self):
        mtype, dest = self._msort.findParentDir('Top.Gear.17x06.HDTV.XviD-FoV')
        self.assertEqual(dest, join(self._dir, 'TV', 'Top.Gear'))
        self.assertEqual(mtype, 'tv')

    def testXVID1(self):
        mtype, dest = self._msort.findParentDir('TrollHunter.2010.LiMiTED.BDRip.XviD-NODLABS')
        self.assertEqual(dest, join(self._dir, 'XVID'))
        self.assertEqual(mtype, 'xvid')

    def testXXX1(self):
        mtype, dest = self._msort.findParentDir('Deep.Anal.Drilling.3.XXX.DVDRip.XviD-Jiggly')
        self.assertEqual(dest, join(self._dir,'XXX'))
        self.assertEqual(mtype, 'xxx')

    def testDVDR1(self):
        mtype, dest = self._msort.findParentDir('Feed.The.Fish.LIMITED.R2.PAL.DVDR-TARGET')
        self.assertEqual(dest, join(self._dir,'DVDR'))
        self.assertEqual(mtype, 'dvdr')

    def testFail1(self):
        mtype, dest = self._msort.findParentDir('asdfasdfasd.fas.fas.fas.fasf-asdf')
        self.assertFalse(dest)
        self.assertFalse(mtype)