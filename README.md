msort
=====================

Simple tool for sorting scene release media folders into grouped subfolders.
Releases are filtered into groups based on regex matching. These groups defined where
to move releases to.

TV shows can get auto sorted into subgroups based on the show names.
eg. testdir/Top.Gear.17x06.HDTV.XviD-FoV -> testdir/TV/Top.Gear

### TestCase Demo

Below is the output of the test suite, it demonstrates roughly what the script
will actually do.

> Matched tv -> Entourage.S08E06.HDTV.Custom.HebSub.XviD-Extinct
> Created dir: testdir/TV/Entourage
> testdir/Entourage.S08E06.HDTV.Custom.HebSub.XviD-Extinct -> testdir/TV/Entourage
> Matched tv -> Top.Gear.17x06.HDTV.XviD-FoV
> Created dir: testdir/TV/Top.Gear
> testdir/Top.Gear.17x06.HDTV.XviD-FoV -> testdir/TV/Top.Gear
> Matched xvid -> TrollHunter.2010.LiMiTED.BDRip.XviD-NODLABS
> Created dir: testdir/XVID
> testdir/TrollHunter.2010.LiMiTED.BDRip.XviD-NODLABS -> testdir/XVID
> Matched xxx -> Deep.Anal.Drilling.3.XXX.DVDRip.XviD-Jiggly
> Created dir: testdir/XXX
> testdir/Deep.Anal.Drilling.3.XXX.DVDRip.XviD-Jiggly -> testdir/XXX