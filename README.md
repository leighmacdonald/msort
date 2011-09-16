msort
=====================

Simple tool for sorting scene release media folders into grouped subfolders.
Releases are filtered into groups based on regex matching. These groups defined where
to move releases to.

TV shows can get auto sorted into subgroups based on the show names.
eg. mv Top.Gear.17x06.HDTV.XviD-FoV /TV/Top.Gear

Demo
==========

    [user@host ~]$ sort.py
    INFO Scanning /mnt/storage/TV
    INFO Scanning /mnt/storage/XVID
    INFO mv /mnt/storage/TV/National.Geographic.Taboo.Misfits.HDTV.XviD-B1LTV /mnt/storage/TV/National.Geographic


Installation
===============

Please note this tool requires python 3 to run. There is no python2 version, although back porting
would be trivial for the current codebase.

    [user@host msort-1.0]$ python3 setup.py install
    running install
    running build
    running build_py
    copying msort/__init__.py -> build/lib/msort
    running build_scripts
    running install_lib
    copying build/lib/msort/__init__.py -> /home/leigh/altroot/lib/python3.2/site-packages/msort
    running install_scripts
    changing mode of /home/leigh/altroot/bin/sort.py to 755
    running install_egg_info
    Removing /home/leigh/altroot/lib/python3.2/site-packages/msort-1.1-py3.2.egg-info
    Writing /home/leigh/altroot/lib/python3.2/site-packages/msort-1.1-py3.2.egg-info
    [leigh@ws msort]$

Configuration
=======================

All configuration options are stored in ~/.msort.conf. By default this file will be automatically
created for you if one doesn't already exist. The config format is the standard ".ini" style.

Any section group that isn't named 'general', 'cleanup', or 'ignored' is considered a "section". Each
section will have a few basic options to configure. The 2 most important of these is the
"sorted" keyword, and the "rxN" keywords, where N is a unique, to the section, integer. If sorted is
true, then matching folders will be sorted into subfolders defined by the (?P<name>) regex capture
grouping. For example if i have the regex: '(?P<name>.+?).S\d{1,2}E\d{1,2}' and the folder name
'Entourage.S08E06.HDTV.Custom.HebSub.XviD-Extinct'. The named capture group would return 'Entourage',
which would be be used for the destination subfolder value. If sorted is false then no suborting is
done and the fodler will simply be placed under the sections folder, which is defined by the sections
'path' keyword. Path definitions are relative to the general basepath.


Usage
=======

All command line options will override any options defined in the main configuration file. I
recommend using the -t option liberally, as it will run through and tell you what it would have done
without making any changes.

    Usage: sort.py [options]

    Options:
      -h, --help    show this help message and exit
      -d, --debug   Enable debugging output level
      -t, --test    Test the changes without actually doing them
      -c, --commit  Commit the changes to disk
      -e, --error   Continue on error


Tests
==========

There is some decent test coverage for the code, however this is reliant on the newer unittest
module only available in python 2.7/3.0+. The unittest2 module which backports some of the newer
features may work, but i have no tested it at all. YMMV. Some test run output is below, it may help
give you a idea of what this tool does.

    move cs_temp cs_tempcs_temp
    DEBUG Set base path to: testdir
    DEBUG Loaded 2 ignore patterns.
    DEBUG Set base path to: testdir
    INFO rmtree testdir/file.avi
    INFO Created dir: testdir/DVDR
    DEBUG Found parent of testdir/Feed.The.Fish.LIMITED.R2.PAL.DVDR-TARGET : testdir/DVDR
    INFO Created dir: testdir/TV/Entourage
    DEBUG Found parent of testdir/Entourage.S08E06.HDTV.Custom.HebSub.XviD-Extinct : testdir/TV/Entourage
    INFO Created dir: testdir/TV/Top.Gear
    DEBUG Found parent of testdir/Top.Gear.17x06.HDTV.XviD-FoV : testdir/TV/Top.Gear
    INFO Created dir: testdir/XVID
    DEBUG Found parent of testdir/TrollHunter.2010.LiMiTED.BDRip.XviD-NODLABS : testdir/XVID
    INFO Created dir: testdir/XXX
    DEBUG Found parent of testdir/Deep.Anal.Drilling.3.XXX.DVDRip.XviD-Jiggly : testdir/XXX
    DEBUG Loaded 4 rule sections and 5 rules.
    DEBUG Loaded 4 rule sections and 5 rules.


TODO
=======================

* Add ability to check if a file/folder is in use before attempting to move it (eg. still downloading), this
isn't very straightforward on Linux unfortunately.
* Fetch media information (synopsis/rating/genre/posters/etc).
* Auto detect type of media based on the name using external resources (imdb/tvrage/etc)