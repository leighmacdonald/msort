import re
from sys import exit
from os import listdir, mkdir, walk, sep
from os.path import exists, join, normpath, abspath, expanduser, isdir
from configparser import RawConfigParser
from shutil import move
import logging

# Make a global logging object.
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
h = logging.StreamHandler()
f = logging.Formatter("%(levelname)s %(message)s")
h.setFormatter(f)
log.addHandler(h)

class ChangeSet:
    def __init__(self, source, dest):
        self.source = source
        self.dest = dest

    def move(self):
        move(self.source, self.dest)


class Config(RawConfigParser):
    """Simple configuration class based on RawConfigParser which will
    load the config file and create one if it doesnt exist.

    It will also parse out the regex values into proper compiled regex
    instances."""
    _DEFAULT = """[general]
basepath = /mnt/storage
commit = false
lock_enabled = true
lock_pattern = ^\.(incomplete|lock|locked)
new_pattern  = ^(.+?\.){2,}.+?-(.*)$

[tv]
path=TV
sorted=true
rx1=(?P<name>.+?).S\d{1,2}E\d{1,2}
rx2=(?P<name>.+?).\d{1,2}X\d{2}

[xvid]
path=XVID
sorted=false
rx1=(?P<name>^.+?[12]\d{3}).+?(dvd|bd)rip.+?Xvid

[dvdr]
path=DVDR
sorted=false
rx1=.+?(PAL|NTSC).DVDR

[xxx]
path=XXX
sorted=false
rx1=.+?\.XXX\.
"""
    
    def __init__(self, configPath="~/.msort.conf"):
        """Load and/or create the config file"""
        RawConfigParser.__init__(self)
        self.confPath = expanduser(configPath)
        if not exists(self.confPath):
            with open(self.confPath, 'w') as f:
                f.write(self._DEFAULT)
                log.info("Wrote default config file to {0}".format(self.confPath))
        self.read(self.confPath)
        self._rules = self.parseRules()

    def getRules(self):
        """ Return the list of rules that have been loaded """
        return self._rules

    def parseRules(self, quiet=False):
        """ Parse the raw configuration options into nicely formatted
        dict's for simple usage. """
        conf = []
        for section in self.filteredSections():
            config = {
                'name'   : section,
                'path'   : self.get(section, 'path'),
                'sorted' : self.getboolean(section, 'sorted'),
                'rx'     : self.getSectionRegex(section)
            }
            conf.append(config)
            if not quiet:
                log.info("Parsed {0} configuration. {1} regexs.".format(section, len(config['rx'])))
        return conf

    def getSectionRegex(self, section):
        """ Build and return a lsit of the regex fields under a given
        section """
        regexList = []
        if self.has_section(section):
            for item, value in list(filter(lambda i: i[0].startswith('rx'), self.items(section))):
                regexList.append(re.compile(value, re.IGNORECASE))
        return regexList

    def filteredSections(self):
        """ Return a list of sections used for parsing only """
        return list(filter(lambda p: p != 'general', self.sections()))

class Location:
    """ Define a location to use, optionally validating it on
    instantiation """
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

    def exists(self):
        return exists(self._path)

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
        """ Initialize the base path and the configuration values """
        if config:
            self.config = config
        else:
            self.config = Config()

        if location:
            self.setBasePath(location)
        else:
            if self.config.has_option('general', 'basepath'):
                path = Location(self.config.get('general', 'basepath'))
                if path.exists():
                    self.setBasePath(path)
                    log.info("Set base path to: {0}".format(path))
                else:
                    log.fatal("Invalid basepath specified")
                    exit(2)
                
        self.rules = self.config.getRules()
        if self.rules:
            log.info("Loaded {0} rule sections and {1} rules.".format(
                len(self.rules),
                sum([len(r['rx']) for r in self.rules])))
        else:
            log.fatal("You must define at least 1 ruleset in the config. ({0})".format(
                self.config.confPath))
            exit(2)

        self.newPattern = re.compile(self.config.get('general', 'new_pattern'))

            
    def setBasePath(self, path):
        """
        Sets the base media path everything is relative to
        """
        self.basePath = path

    def genFileList(self):
        """
        Generate a list of files to scan through
        """
        return listdir(self.basePath.path)

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

    def findParentDir(self, path, dest=None, mtype=None):
        """
        Find the parent path of the media folder supplied
        """
        for rule in self.rules:
            for rx in rule['rx']:
                match = rx.search(path)
                if match:
                    base = self.config.get('general', 'basepath')
                    if not rule['sorted']:
                        dest = join(base, rule['path'])
                    else:
                        dest  = join(base, rule['path'], match.groupdict()['name'])
                    mtype = rule['name']
                    if exists(join(dest, path)):
                        return False, False
                    else:
                        #print("Matched {0} -> {1}".format(rule['name'], path))
                        break
        if dest:
            if not exists(dest):
                pcs = parse_path(dest)
                for i, v in enumerate(pcs):
                    try:
                        d = "{0}{1}".format(sep, sep.join(pcs[:i+1]))
                        mkdir(d)
                    except OSError as err:
                        if err.args[0] == 17:
                            pass
                        else:
                            raise
                log.info(("Created dir: {0}".format(dest)))
            releasePath = join(self.basePath.path, path)
            files = self.getReleaseFiles(releasePath)
            #print(files)
            if any(map(self.isLocked, files)):
                log.error("LOCKED!")
                mtype, dest = False, False
            else:
                pass
                #print(("{0} -> {1}".format(releasePath, dest)))
            return mtype, dest
        else:
            return False, False

    def move(self, src, dest):
        """ Move a release to a new destination """
        move(src, dest)
        
    def getReleaseFiles(self, folder):
        """ Get a list of files within the releases folder """
        filelist = []
        for root, dirs, files in walk(folder):
            #print root
            #print dirs
            #print files
            map(filelist.append, [ join(root, f) for f in files ])
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
            log.exception(err)
            return True

def parse_path(path):
    """ Parse a path into separate pieces
    This probably doesnt work very well under windows?"""
    return normpath(abspath(path)).split(sep)[1:]