from os import mkdir, remove, rename
from os.path import exists, join
from shutil import rmtree
try:
    import unittest2 as unittest
except ImportError:
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
            'file.avi',
            'Crave.S01E01.HDTV.XviD-SYS',
            'The.Terrorist.2010.720p.BluRay.x264-aAF',
            'TrollHunter.2010.LiMiTED.BDRip.XviD-NODLABS',
            'Tyler.Perrys.Laugh.To.Keep.From.Crying.2009.DVDRip.XviD-IGUANA',
            'Deep.Anal.Drilling.3.XXX.DVDRip.XviD-Jiggly',
            'Anal.Ecstasy.XXX.NTSC.DVDR-EvilAngel',
            'Feed.The.Fish.LIMITED.R2.PAL.DVDR-TARGET',
            'Top.Gear.17x06.HDTV.XviD-FoV'
        ]
        cls._dir = 'testdir'
        if not exists(cls._dir):
            mkdir(cls._dir)
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

    def testCleanup(self):
        f = self._msort.findCleanupFiles(self._dir)
        self.assertListEqual(['file.avi'], f)
        cs = [msort.ChangeSet.remove(join(self._dir, f)) for f in self._msort.findCleanupFiles(self._dir)]
        for c in cs:
            c(commit=True)
            self.assertFalse(exists(c.source))
        
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
        self.assertTrue(not any([dest, mtype]))

    def testCleanupEmpty(self):
        p = msort.Location(self._dir, 'cleanme', validate=False)
        if not exists(p.path): mkdir(p.path)
        self.assertTrue(self._msort.dirIsEmpty(p))
        open(join(p.path, 'test.file'), 'w').write('Hi')
        self.assertFalse(self._msort.dirIsEmpty(p))
        if exists(p.path): rmtree(p.path)

class TestFileOpenLinux(unittest.TestCase):
    def testFOpen(self):
        """
        todo: Make this actually work..
        :return:
        """
        filename = '.OpenFile'
        with open(filename, 'a+') as f:
            f.write('Hi')
            with open(filename) as rof:
                rename(filename, "{0}_".format(filename))
                self.assertTrue(exists("{0}_".format(filename)))
                self.assertFalse(exists("{0}".format(filename)))


    def tearDown(self):
        [remove(f) for f in ['.OpenFile', '.OpenFile_' ] if exists(f)]
