#!/usr/bin/python
from __future__ import print_function
from logging import basicConfig, DEBUG, INFO, getLogger
from optparse import OptionParser
from msort.conf import Config
from msort.filesystem import DirectoryScanner
from msort.check.empty import EmptyCheck
from msort.check.release import ReleaseCheck

parser = OptionParser(version='2.0')
parser.add_option('-d', '--debug', dest="debug", action="store_true", default=False, help="Enable debugging output level")

options, args = parser.parse_args()

# Setup Logger
log_level = DEBUG if options.debug else INFO
basicConfig(level=log_level)
log = getLogger(__name__)
log.info('Initializing!')

conf = Config()

scanner = DirectoryScanner(conf)
scanner.registerChecker(EmptyCheck(conf))
scanner.registerChecker(ReleaseCheck(conf))
sections = conf.filteredSections()
changes = {}
for section in sections:
    changes[section] = scanner.find(section)
for key, value in changes.items():
    for c in value:
        log.debug(c)