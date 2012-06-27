import unittest
from msort import transform

class TransformTest(unittest.TestCase):
    def test_splitucwords(self):
        s = 'RegularShow'
        self.assertEqual(['Regular','Show'], transform.split_uc_words(s))

    def test_ucfirst(self):
        self.assertEqual('Lower', transform.ucfirst('lower'))

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

if __name__ == '__main__':
    unittest.main()
