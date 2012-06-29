msort (mediasort)
=====================

Media sort is meant to be used as a tool that will sort folders and files matching
certain specifications, into logical folder trees. Its currently tailored to TV and
Movie formats, but there is no restrictions on this and its quite flexible.

Example of what can be accolplish:

- TV shows can get auto sorted into subgroups based on the show names. eg. mv Top.Gear.17x06.HDTV.XviD-FoV /TV/Top.Gear
- Detect empty files and folders and mark them for deletion
- Check if a file is in use before trying to perform a operation to prevent files being altered that are being used by other processes.


Installation
===============

Installation is carried out using the standard distutils formula as shown below.

    [root@host msort]# python setup.py install
    running install
    <snip>
    Writing /home/leigh/altroot/lib/python3.2/site-packages/msort-1.1-py3.2.egg-info
    [root@ws msort]#

Configuration
=======================

All configuration options are stored in ~/.msort.conf. By default this file will be automatically
created for you if one doesn't already exist. The config format is the standard ".ini" style.

Any section group that isn't named 'general', 'cleanup', 'ignored' or 'logging' is considered a "section". Each
section will have a few basic options to configure. The most important of these is the
"sorted" keyword, the "rxN" keywords, where N is a unique, to the section, integer as well as the source and dest
keywords. If sorted is enabled on the section, then matching folders will be sorted into subfolders defined by
the (?P<name>) regex capture grouping. For example if i have the regex: '(?P<name>.+?).S\d{1,2}E\d{1,2}' and the folder name
'Entourage.S08E06.HDTV.Custom.HebSub.XviD-Extinct'. The named capture group would return 'Entourage',
which would be be used for the destination subfolder value. If sorted is false then no sub sorting is
done and the folder will simply be placed under the sections destination, which is defined by the sections
'dest' keyword. Path definitions should be absolute, but this isnt a strict requirement.


Usage
=======

    Usage: mediasort.py [options]

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -d, --debug           Enable debugging output level
      -y, --yes             Answer yes for all question, autocommit changes found
      -c CONFIG_FILE, --config=CONFIG_FILE
                            Set an alternate config file path

And a trimmed down example of it being run:

    [user@ws msort] $ mediasort.py -c /home/username/.msort.conf
    Reading config: /home/username/.msort.conf
    Loaded 1 rule sections and 5 rules.
    Registered check instance: InUseCheck
    Registered check instance: EmptyCheck
    Registered check instance: ReleaseCheck
    Starting scan of section TV: /export/storage/TV
    <snip>
    Check matched: MoveOperation /export/storage/TV/RegularShow.s03e28.AccessDenied.mp4 /export/storage/TV/Regular.Show
    Detected In-Use path, Skipping: /export/storage/TV/RegularShow.s03e29.MuscleMentor.mp4
    Check matched: MoveOperation /export/storage/TV/the.bleak.old.shop.of.stuff.s01e01.hdtv.xvid-ftp.avi /export/storage/TV/The.Bleak.Old.Shop.Of.Stuff
    Check matched: MoveOperation /export/storage/TV/the.daily.show.2012.03.01.hdtv.xvid-fqm.avi /export/storage/TV/The.Daily.Show
    Found 100 total changes to be executed
    Apply changes found (100)? [Y/n]: <enter>
    Executing: MoveOperation /export/storage/TV/portlandia.s02e10.hdtv.xvid-fqm.avi /export/storage/TV/Portlandia
    <snip>
    Executing: MoveOperation /export/storage/TV/the.daily.show.2012.03.01.hdtv.xvid-fqm.avi /export/storage/TV/The.Daily.Show


Tests
==========

There is quite good test coverage currently. About 95%. Tests run under python2/3 ok. There
is likly issues on windows for the tests though.

    [user@ws msort] $ python setup.py test
    <snip>
    ----------------------------------------------------------------------
    Ran 39 tests in 1.038s

    OK
    [user@ws msort] $



TODO
=======================

* Fetch media information (synopsis/rating/genre/posters/etc).
* Auto detect type of media based on the name using external resources (imdb/tvrage/etc)