import re
from os import listdir, mkdir, walk, sep
from os.path import exists, join, normpath, abspath, expanduser
from configparser import RawConfigParser
from shutil import move

class Config(RawConfigParser):
    """Simple configuration class based on RawConfigParser which will
    load the config file and create one if it doesnt exist"""
    _DEFAULT = """
    [general]
    basepath = /home/leigh/testdir
    commit = false

    [tv]
    path=TV
    sorted=true
    rx1=(?P<name>.+?).S\d{1,2}E\d{1,2}
    rx2=(?P<name>.+?).\d{1,2}X\d{2}
    
    [xvid]
    path=XVID
    sorted=false
    rx1=(?P<name>^.+?[12]\d{3}).+?(dvd|bd)rip.+?Xvid

    [xxx]
    path=XXX
    sorted=false
    rx1=.+?\.XXX\.
    """
    
    def __init__(self):
        """Load and/or create the config file"""
        RawConfigParser.__init__(self)
        confPath = expanduser("~/.msort.conf")
        if not exists(confPath):
            with open(confPath, 'w') as f:
                f.write(self._DEFAULT)
                print("Wrote default config file to {0}".format(confPath))
        self.read(confPath)
        self._rules = self.parseRules()

    def getRules(self):
        return self._rules

    def parseRules(self):
        conf = []
        for section in self.filteredSections():
            config = {
                'name'   : section,
                'path'   : self.get(section, 'path'),
                'sorted' : self.getboolean(section, 'sorted'),
                'rx'     : self.getSectionRegex(section)
            }
            conf.append(config)
            print("Parsed {0} configuration. {1} regexs.".format(section, len(config['rx'])))
        return conf

    def getSectionRegex(self, section):
        regexList = []
        if self.has_section(section):
            for item, value in list(filter(lambda i: i[0].startswith('rx'), self.items(section))):
                regexList.append(re.compile(value, re.IGNORECASE))
        return regexList

    def filteredSections(self):
        return list(filter(lambda p: p != 'general', self.sections()))

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
        Return the current path as a string representation
        """
        return self._path


    
class MSorter:
    """
    Media sorting class
    """

    def __init__(self, location=None, config=None):
        if location: self.setBasePath(location)
        if config:
            self.config = config
        else:
            self.config = Config()
        self.rules = self.config.getRules()

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
        return releases #list(filter(self.isNew, releases))

    def _genPath(self, filename):
        """
        Generate a path from the basepath
        """
        return "{0}/{1}".format(self.basePath, filename)

    def findParentDir(self, path, dest=None):
        """
        Find the parent path of the media folder supplied
        """
        mtype = None
        for rule in self.rules:
            for rx in rule['rx']:
                match = rx.search(path)
                if match:
                    if not rule['sorted']:
                        dest = rule['path']
                    else:
                        dest  = join(rule['path'],match.groupdict()['name'])
                    mtype = rule['name']
                    print("Matched {0} -> {1}".format(rule['name'], path))
                    break
        if dest:
            destpath = self._genPath(dest)
            if not exists(destpath):
                pcs = parse_path(destpath)
                for i, v in enumerate(pcs):
                    try:
                        d = "{0}{1}".format(sep, sep.join(pcs[:i+1]))
                        mkdir(d)
                    except OSError as err:
                        if err.args[0] == 17:
                            pass
                        else:
                            raise
                #mkdir(destpath)
                print(("Created dir: {0}".format(destpath)))
                #return "{0} -> {1}".format(self._genPath(path), destpath)
            #move(self._genPath(path), destpath)
            releasePath = self._genPath(path)
            files = self.getReleaseFiles(releasePath)
            #print(files)
            if any(map(self.isLocked, files)):
                print("LOCKED!")
                dest = False
            else:
                print(("{0} -> {1}".format(self._genPath(path), destpath)))
                dest = destpath
            return mtype, dest
        else:
            return False, False

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
        except IOError as err:
            print(err)
            return True


def parse_path(path):
    return normpath(abspath(path)).split(sep)[1:]