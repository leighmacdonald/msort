#!/bin/env python3
from sys import argv
from os.path import expanduser, exists, join
from msort import MSorter, Location, Config, ChangeSet, log

defaultPath = expanduser("~/Music")
path = argv[1] if len(argv) > 1 else defaultPath if exists(defaultPath) else expanduser("~/")
c = Config()
m = MSorter(config=c)
#print(m.genFileList())
changes = []
for section in c.filteredSections():
    newPath = Location(join(c.get('general', 'basepath'), c.get(section, 'path')))
    m.setBasePath(newPath)
    log.info("Scanning {0}".format(newPath))
    for p in m.filterIgnored(m.findNew(m.genFileList())):
        mtype, path = m.findParentDir(p)
        if mtype and path:
            releasePath = join(m.basePath.path, p)
            log.info("Moving {0} -> {1}".format(releasePath, path))
            changes.append(ChangeSet(releasePath, path))
commit = m.config.getboolean('general', 'commit')
for change in changes:
    if commit:
        log.info('COMMITTED: {0}'.format(change))
    else:
        log.info('SKIPPED: {0}'.format(change))