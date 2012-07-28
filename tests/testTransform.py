import unittest
from msort import transform

class TransformTest(unittest.TestCase):
    def test_splitucwords(self):
        self.assertEqual(['Regular','Show'], transform.split_uc_words('RegularShow'))

    def test_splitucupperwords(self):
        self.assertEqual(['NOVA'], transform.split_uc_words('NOVA'))

    def test_ucfirst(self):
        self.assertEqual('Lower', transform.ucfirst('lower'))
        self.assertEqual('', transform.ucfirst(''))

    def test_upperwords(self):
        self.assertEqual('Upper.Words', transform.upperwords('upper.words'))

    def test_cleanup(self):
        res = transform.cleanup('Adventure Time - 4x07 - In Your Footsteps')
        self.assertEqual('Adventure.Time.4x07.In.Your.Footsteps', res)

    def test_cleanupTrailing(self):
        res = transform.cleanup('Adventure Time - 4x07 - In Your Footsteps.')
        self.assertEqual('Adventure.Time.4x07.In.Your.Footsteps', res)

    def test_cleanup_two(self):
        res = transform.cleanup('RegularShow.s03e16.ButtDial.mp4')
        self.assertEqual('Regular.Show.S03e16.Butt.Dial.Mp4', res)

    def test_cleanup_upper(self):
        res = transform.split_uc_words('NOVA.S39E16.480p.HDTV.x264-mSD.mkv')
        self.assertEqual('NOVA', res[0])

if __name__ == '__main__':    unittest.main()
