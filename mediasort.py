#!/usr/bin/python
from __future__ import print_function
from logging import basicConfig, DEBUG, INFO
from optparse import OptionParser

from msort.conf import Config
from msort.log import getLogger
from msort.filesystem import DirectoryScanner
from msort.check.empty import EmptyCheck
from msort.check.release import ReleaseCheck


parser = OptionParser(version='2.0')
parser.add_option('-d', '--debug', dest="debug", action="store_true", default=False, help="Enable debugging output level")

options, args = parser.parse_args()

# Setup Logger
log = getLogger(__name__)
log_level = DEBUG if options.debug else INFO
log.setLevel(log_level)
#if log_level == DEBUG:
#    basicConfig(level=log_level)
#else:
#    log.setLevel(log_level)
basicConfig(level=log_level, format='%(message)s')


conf = Config()

scanner = DirectoryScanner(conf)
scanner.registerChecker(EmptyCheck(conf))
scanner.registerChecker(ReleaseCheck(conf))
sections = conf.filteredSections()
changes = {}
for section in sections:
    changes[section] = scanner.find(section)
total_changes = sum([len(x) for x in changes.values()])
log.info('Found {0} total changes to be executed'.format(total_changes))

for key, value in changes.items():
    for c in value:
        log.debug(c)