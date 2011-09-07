#!/bin/env python3
from sys import argv
from os.path import expanduser, exists, join
from msort import MSorter, Location, Config, ChangeSet

defaultPath = expanduser("~/Music")
path = argv[1] if len(argv) > 1 else defaultPath if exists(defaultPath) else expanduser("~/")
c = Config()
m = MSorter(config=c)
#print(m.genFileList())
changes = []
for section in c.filteredSections():
    newPath = Location(join(c.get('general', 'basepath'), c.get(section, 'path')))
    m.setBasePath(newPath)
    print("Scanning {0}".format(newPath))
    for p in m.findNew(m.genFileList()):
        mtype, path = m.findParentDir(p)
        if mtype and path:
            releasePath = join(m.basePath.path, p)
            print("Moving {0} -> {1}".format(releasePath, path))
            changes.append(MS)
