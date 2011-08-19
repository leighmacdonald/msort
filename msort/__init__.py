import fcntlmodule as fcntl
import re
from os import listdir, mkdir, O_EXLOCK
from os.path import exists
from shutil import move

class Location:
    def __init__(self, path, validate=True):
        if validate and not exists(path):
            raise IOError('Invalid path specified: {0}'.format(path))
        self._path = path

    @property
    def path(self):
        return self._path

    def __str__(self):
        return self._path


    
class MSorter:
    newPattern = re.compile(r"""S\d{1,2}E\d{1,2}""", re.IGNORECASE)
    tvPattern  = re.compile(r"""(?P<name>.+?).S\d{1,2}E\d{1,2}""", re.IGNORECASE)
    
    def __init__(self, location=None):
        if location:
            self.setBasePath(location)

    def setBasePath(self, path):
        self.basePath = path

    def genFileList(self):
        self._fileList = listdir(self.basePath.path)
        return self._fileList

    def sort(self):
        if not self._fileList:
            raise AssertionError("No file list to work on")

    def isNew(self, file):
        return self.newPattern.search(file)

    def findNew(self, releases):
        return filter(self.isNew, releases)

    def _genPath(self, filename):
        return "{0}/{1}".format(self.basePath, filename)

    def findParentDir(self, path, dest=None):
        tv = self.tvPattern.search(path)
        if tv:
            dest = tv.groupdict()['name']

        if dest:
            destpath = self._genPath(dest)
            if not exists(destpath):
                mkdir(destpath)
                print "Created dir: {0}".format(destpath)
            #return "{0} -> {1}".format(self._genPath(path), destpath)
            move(self._genPath(path), destpath)
            print "{0} -> {1}".format(self._genPath(path), destpath)

    def isLocked(self, filename):
        """
        Check to see if a file is in a locked state (in use)
        """
        try:
            return bool(open(filename, 'a'))
        except IOError:
            return False