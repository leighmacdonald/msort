from re import compile as rxcompile, IGNORECASE
from sys import exit
from os import listdir, mkdir, walk, sep
from os.path import exists, join, normpath, abspath, expanduser
from configparser import RawConfigParser
from shutil import move
from logging import getLogger, Formatter, StreamHandler, INFO

def logInit(config=None):
    global log
    log = getLogger(__name__)
    if config and config.has_section('logging'):
        # Make a global logging object.
        level = int(config.getSafe('logging', 'level', INFO))
        log.setLevel(level)
        h = StreamHandler()
        f = Formatter("%(levelname)s %(message)s")
        h.setFormatter(f)
        log.addHandler(h)
    else:
        log.setLevel(INFO)
    return log
log = logInit()

class ChangeSet:
    def __init__(self, source, dest):
        self.source = source
        self.dest = dest

    def move(self):
        move(self.source, self.dest)

    def __str__(self):
        return '{0} -> {1}'.format(self.source, self.dest)

class ConfigError(Exception): pass

class Config(RawConfigParser):
    """Simple configuration class based on RawConfigParser which will
    load the config file and create one if it doesnt exist.

    It will also parse out the regex values into proper compiled regex
    instances."""
    _DEFAULT = """[general]
basepath = /mnt/storage
commit = true
lock_enabled = true
lock_pattern = ^\.(incomplete|lock|locked)
new_pattern  = ^(.+?\.){2,}.+?-(.*)$

[logging]
enabled=true
# NOTSET = 0 | DEBUG = 10 | INFO = 20 | WARN = 30 | ERROR = 40 | FATAL = 50
level=10
format="%(levelname)s %(message)s"

[ignored]
rx1=(.avi|.mkv)$
rx2=(.txt|.nfo)$

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
    
    def __init__(self, configPath="~/.msort.conf", skip=['general', 'ignored', 'logging']):
        """Load and/or create the config file"""
        RawConfigParser.__init__(self)
        self.skip = skip
        self.confPath = expanduser(configPath)
        if not exists(self.confPath):
            try:
                pcs = self.confPath.split(sep)
                dirPath = pcs[:-1]
                p = sep
                for path in dirPath:
                    p = join(p, path)
                mkdirp(p)
                with open(self.confPath, 'w') as f:
                    f.write(self._DEFAULT)
            except IOError as err:
                raise ConfigError(err.strerror)
            except OSError as err:
                raise ConfigError('Cannot create configuration base directory {0}'.format(p))
        self.read(self.confPath)
        self._rules = self.parseRules()

    def getRules(self):
        """ Return the list of rules that have been loaded """
        return self._rules

    def parseRules(self):
        """ Parse the raw configuration options into nicely formatted
        dict's for simple usage. """
        conf = []
        for section in self.filteredSections():
            conf.append({
                'name'   : section,
                'path'   : self.get(section, 'path'),
                'sorted' : self.getboolean(section, 'sorted'),
                'rx'     : self.getSectionRegex(section)
            })
        return conf

    def getSectionRegex(self, section):
        """ Build and return a lsit of the regex fields under a given
        section """
        regexList = []
        if self.has_section(section):
            for item, value in filter(lambda i: i[0].startswith('rx'), self.items(section)):
                regexList.append(rxcompile(value, IGNORECASE))
        return regexList

    def filteredSections(self):
        """ Return a list of sections used for parsing only """
        return filter(lambda p: p not in self.skip, self.sections())

    def getSafe(self, section, option, default=False):
        if self.has_section(section) and self.has_option(section, option):
            return self.get(section, option)
        return default


class Location:
    """ Define a location to use, optionally validating it on
    instantiation """
    def __init__(self, *paths, validate=True):
        path = join(paths[0])
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
        log = logInit(self.config)

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
            else:
                log.fatal('basepath must be defined in [general] ({0})'.format(
                    self.config.confPath)
                )
                exit(2)
        self.rules = self.config.getRules()
        if self.rules:
            log.info("Loaded {0} rule sections and {1} rules.".format(
                len(self.rules), sum([len(r['rx']) for r in self.rules]))
            )
        else:
            log.fatal("You must define at least 1 ruleset in the config. ({0})".format(
                self.config.confPath))
            exit(2)

        self.newPattern = rxcompile(self.config.get('general', 'new_pattern'))
        if self.config.has_section('ignored'):
            self.ignores = self.config.getSectionRegex('ignored')
            log.debug('Loaded {0} ignore patterns.'.format(len(self.ignores)))
        else:
            log.info('No ignore patterns defined')

            
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

    def filterIgnored(self, paths):
        valid = []
        for path in paths:
            if not any([rx.search(path) for rx in self.ignores]):
                valid.append(path)
        return valid
    
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
                        dest = join(base, rule['path'], match.groupdict()['name'])
                    mtype = rule['name']
                    if exists(join(dest, path)):
                        return False, False
                    else:
                        #print("Matched {0} -> {1}".format(rule['name'], path))
                        break
        if dest:
            if not exists(dest):
                mkdirp(dest)
            releasePath = join(self.basePath.path, path)
            files = self.getReleaseFiles(releasePath)
            if any(map(self.isLocked, files)):
                log.error("LOCKED!")
                mtype, dest = False, False
            else:
                log.debug("Found parent of {0} : {1}".format(releasePath, dest))
            return mtype, dest
        else:
            return False, False

    def move(self, src, dest):
        """ Move a release to a new destination """
        move(src, dest)
        
    def getReleaseFiles(self, folder, filelist=[]):
        """ Get a list of files within the releases folder """
        [ map(filelist.append, [ join(root, f) for f in files ]) for root, dirs, files in walk(folder) ]
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

def mkdirp(dest):
    new = False
    pcs = parse_path(dest)
    for i, v in enumerate(pcs):
        try:
            d = "{0}{1}".format(sep, sep.join(pcs[:i+1]))
            if not exists(d):
                mkdir(d)
                new = True
        except OSError as err:
            if err.args[0] == 17:
                pass
            else:
                raise
    if new:
        log.info("Created dir: {0}".format(dest))