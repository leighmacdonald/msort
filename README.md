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


Usage
=======

    Usage: sort.py [options]

    Options:
      -h, --help    show this help message and exit
      -d, --debug   Enable debugging output level
      -t, --test    Test the changes without actually doing them
      -c, --commit  Commit the changes to disk
      -e, --error   Continue on error
