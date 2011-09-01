from msort import MSorter, Location

m = MSorter(Location('/home/leigh/Music'))
map(m.findParentDir, m.findNew(m.genFileList()))
