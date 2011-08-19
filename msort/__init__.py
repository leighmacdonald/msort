import fcntlmodule as fcntl
import re
from os import listdir, mkdir, walk
from os.path import exists, join
from shutil import move

class Location:
    """
    Location class
    """

    def __init__(self, path, validate=True):
        if validate and not exists(path):
            raise IOError('Invalid path specified: {0}'.format(path))
        self._path = path

    @property
    def path(self):
        """
        return the current path specified
        """
        return self._path

    def __str__(self):
        """
        Return the current path as a string prepresentation
        """
        return self._path


    
class MSorter:
    """
    Media sorting class
    """
    newPattern = re.compile(r"""S\d{1,2}E\d{1,2}""", re.IGNORECASE)
    tvPattern  = re.compile(r"""(?P<name>.+?).S\d{1,2}E\d{1,2}""", re.IGNORECASE)
    
    def __init__(self, location=None):
        if location: self.setBasePath(location)

    def setBasePath(self, path):
        """
        Sets the base media path everything is relative to
        """
        self.basePath = path

    def genFileList(self):
        """
        Generate a list of files to scan through
        """
        self._fileList = listdir(self.basePath.path)
        return self._fileList

    def sort(self):
        """
        Perform the actual act
        """
        if not self._fileList:
            raise AssertionError("No file list to work on")

    def isNew(self, file):
        """
        Do a "new check" on the given file. Currently just looks for "SNNENN"
        """
        return self.newPattern.search(file)

    def findNew(self, releases):
        """
        Find any files that look "new", this means unsorted, not
        necessarily new files.
        """
        return filter(self.isNew, releases)

    def _genPath(self, filename):
        """
        Generate a path from the basepath
        """
        return "{0}/{1}".format(self.basePath, filename)

    def findParentDir(self, path, dest=None):
        """
        Find the parent path of the media folder supplied
        """
        tv = self.tvPattern.search(path)
        if tv:
            dest = tv.groupdict()['name']

        if dest:
            destpath = self._genPath(dest)
            if not exists(destpath):
                mkdir(destpath)
                print "Created dir: {0}".format(destpath)
            #return "{0} -> {1}".format(self._genPath(path), destpath)
            #move(self._genPath(path), destpath)
            files = self.getReleaseFiles(self._genPath(path))
            print files
            if any(map(self.isLocked, files)):
                print "LOCKED!"
            else:
                print "{0} -> {1}".format(self._genPath(path), destpath)

    def getReleaseFiles(self, folder):
        filelist = []
        for root, dirs, files in walk(folder):
            #print root
            #print dirs
            #print files
            for f in files:
                filelist.append(join(root, f))
        return filelist

    def isLocked(self, filename):
        """
        Check to see if a file is in a locked state (in use)
        """
        try:
            file = open(filename, 'a+')
            if file:
                return False
            return True
        except IOError, err:
            print err
            return True