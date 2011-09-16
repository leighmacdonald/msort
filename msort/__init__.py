from re import compile as rxcompile, IGNORECASE
from sys import exit
from os import listdir, mkdir, walk, sep, readlink, access, EX_OK, remove
from os.path import exists, join, normpath, abspath, expanduser, isdir, isfile
from shutil import rmtree
try:
    from configparser import RawConfigParser, NoOptionError, NoSectionError
except ImportError:
    from ConfigParser import RawConfigParser, NoOptionError, NoSectionError
from shutil import move
from logging import getLogger, Formatter, StreamHandler, INFO, basicConfig


def logInit(config=None):
    """Initialize the logger class
    :param config: Config instance
    :type config: Config
    :return: logger instance
    :rtype: RootLogger
    """
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
    """ A simple changeset to be executed """
    def __init__(self, src, dst=None, operation=move):
        """
        :param src: Source file/dir
        :type src: string
        :param dst: Destination file/dir
        :type dst: string
        """
        self.source = src
        self.dest = dst
        if not hasattr(operation, '__call__'):
            raise AttributeError('Operation must be callable')
        self.oper = operation

    @classmethod
    def remove(cls, path):
        """ Return a changeset to remove the given file or path from the filesystem

        :param cls: ChangeSet
        :type cls: ChangeSet
        :param path:
        :type path: str
        :return: Changeset instance to be executed
        :rtype: ChangeSet
        """
        if not exists(path):
            raise OSError('Invalid path: {0}'.format(path))
        if isdir(path):
            o = rmtree
        elif isfile(path):
            o = remove
        return cls(path, operation=o)

    def __call__(self, *args, **kwargs):
        """ Execute the operation under the operation property

        :param commit: Actually run the operation?
        :type commit: bool
        """
        commit = kwargs['commit'] if 'commit' in kwargs else False
        if commit:
            log.info(self)
            if self.dest:
                return self.oper(self.source, self.dest)
            else:
                return self.oper(self.source)
        else:
            log.info(self)
            
    def __str__(self):
        """ Show a simple string example of the operation to be performed

        :return: shell like representation of the operation
        :rtype: str
        """
        return '{2} {0} {1}'.format(self.source, self.dest if self.dest else '', self.oper.__name__)

class ConfigError(Exception):
    """
    Thrown on configuration issues
    """
    pass

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
error_continue=false

[cleanup]
enable = true
delete_empty = true
rx1=(\.avi|\.mkv)$

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
    
    def __init__(self, configPath="~/.msort.conf", skiplist=['general', 'ignored', 'logging', 'cleanup']):
        """ Initialize the configuration. If a existing one doesnt exit a new one will be created
        in, by default, the users home directory, unless otherwise specified by the configPath
        parameter

        :param configPath: Location of the config file
        :param skip: List of filtered sections to skip when parsing for rules
        """
        RawConfigParser.__init__(self)
        self.skip = skiplist
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
            except OSError:
                raise ConfigError('Cannot create configuration base directory {0}'.format(p))
        self.read(self.confPath)
        self._rules = self.parseRules()

    def getRules(self):
        """Return the loaded ruleset

        :return: List of rules loaded
        :rtype: list
        """
        return self._rules

    def parseRules(self):
        """ Parse the raw configuration options into nicely formatted
        dict's for simple usage.

        :return: list of option dicts
        :rtype: list
        """
        conf = list()
        for section in self.filteredSections():
            conf.append({
                'name'   : section,
                'path'   : self.get(section, 'path'),
                'sorted' : self.getboolean(section, 'sorted'),
                'rx'     : self.getSectionRegex(section)
            })
        if conf:
            log.debug("Loaded {0} rule sections and {1} rules.".format(
                len(conf), sum([len(r['rx']) for r in conf]))
            )
        return conf

    def getSectionRegex(self, section):
        """ Build and return a list of the regex fields for the section
        provided. All fields starting with 'rx' are considered valid regex
        rules to attempt to use.

        :param section: Config file section name
        :type section: string
        :return: List of regular expressions
        :rtype: list
        """
        regexList = []
        if self.has_section(section):
            for item, value in self._rxFilter(self.items(section)):
                regexList.append(rxcompile(value, IGNORECASE))
        return regexList

    def _rxFilter(self, iter):
        """ Filter to only regex items
        
        :param iter: Regex configuration tuples
        :type iter: list
        :return:
        """
        return filter(lambda i: i[0].startswith('rx'), iter)
    
    def filteredSections(self):
        """ Get a list of valid ruleset sections

        :return: Filtered sections
        :rtype: filter
        """
        return filter(lambda p: p not in self.skip, self.sections())

    def getNextRxId(self, section, findid=1):
        """
        Return the next available free regex item key
        :param findid: Starting index
        :type findid: int
        :param section: Section to look through
        :type section: string
        :return: section regex key
        :rtype: string
        """
        while 'rx{0}'.format(findid) in [id for id, value in self._rxFilter(self.items(section))]:
            findid += 1
        return 'rx{0}'.format(findid)

    def getSafe(self, section, option, default=False):
        """ Get a config value providing a default value if it doesnt exist
        
        :param section: Config section name
        :type section: string
        :param option: Config option name
        :param default: string
        :return: config value
        :rtype: string
        """
        if self.has_section(section) and self.has_option(section, option):
            return self.get(section, option)
        return default

    def addRule(self, section, rule):
        """ Add a new regex rule to the configuration of a given section

        :param section: configuration section
        :type section: str
        :param rule: Regex pattern
        :type rule: str
        :return: Add status
        :rtype: bool

        """
        pass

    def getRuleList(self, section):
        if not section in self.filteredSections():
            raise ValueError('Invalid section given')
        secs = self._rxFilter(self.items(section))
        return secs


class Location:
    """ Define a location to use, optionally validating it on
    instantiation """
    def __init__(self, *args, **kwargs):
        """ Initialize and optionally validate the path given
        
        :param paths: N number of paramerters to be joined into a complete path
        :type paths: string
        :param validate: Check the exitence of the path
        :type validate: bool
        """
        validate = kwargs['validate'] if 'validate' in kwargs else True
        path = ''
        for p in args:
            path = join(path, p)
        if validate and not exists(path):
            raise IOError('Invalid path specified: {0}'.format(path))
        self._path = path

    @property
    def path(self):
        """ Get the current path specified

        :return: Given path
        :rtype: string
        """
        return self._path

    def exists(self):
        """ Check if the current location exists
        :return: Existence status
        :rtype: bool
        """
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
        """ Initialize the base path and the configuration values

        :param location: Base sort path to look through
        :type location: Location
        :param config: Config instance
        :type: Config
        """
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
                else:
                    log.fatal("Invalid basepath specified")
                    exit(2)
            else:
                log.fatal('"basepath" must be defined in [general] ({0})'.format(
                    self.config.confPath)
                )
                exit(2)
        self.rules = self.config.getRules()
        if not self.rules:
            log.fatal("You must define at least 1 ruleset in the config. ({0})".format(
                self.config.confPath))
            exit(2)
        if not self.config.has_option('general', 'new_pattern'):
            log.fatal('"new_pattern" must be defined in [general] ({0})'.format(
                    self.config.confPath))
            exit(2)
        self.newPattern = rxcompile(self.config.get('general', 'new_pattern'))
        if self.config.has_section('ignored'):
            self.ignores = self.config.getSectionRegex('ignored')
            log.debug('Loaded {0} ignore patterns.'.format(len(self.ignores)))
        else:
            log.info('No ignore patterns defined')

            
    def setBasePath(self, path):
        """ Sets the base media path everything is relative to

        :param path: Base path used for searching
        :type path: Location
        """
        self.basePath = path
        log.debug("Set base path to: {0}".format(path))

    def genFileList(self, path=None):
        """
        Generate a list of files to scan through

        :return: File list for base directory
        :rtype: list
        """
        if path: return listdir("{0}".format(path))
        return listdir(self.basePath.path)

    def filterIgnored(self, paths):
        """ Remove any ignored files from the given list of files

        :param paths: List of files to check
        :type paths: list
        :return: List of validated files
        :rtype: list
        """
        valid = []
        for path in paths:
            if not any([rx.search(path) for rx in self.ignores]):
                valid.append(path)
        return valid
    
    def isNew(self, file):
        """ Do a "new check" on the given file. Currently just looks for "SNNENN"
        
        :param file: File to check
        :type file: str
        :return: New status
        :rtype: bool
        """
        return bool(self.newPattern.search(file))

    def findCleanupFiles(self, path, filelist=[]):
        """
        Find files to delete from disk
        
        :param path:
        :param filelist:
        :return: Deleteable files
        :rtype: list
        """
        rxlist = self.config.getSectionRegex('cleanup')
        for f in self.genFileList(path):
            [filelist.append(f) for rx in rxlist if rx.search(f)]
        return list(set(filelist))

    def dirIsEmpty(self, path):
        """ Check for a directory's empty-ness

        :param path: Full path to a directory to check
        :type path: Location
        :return: empty status
        :rtype: bool
        """
        if exists(path.path) and isdir(path.path):
            files = listdir(path.path)
            return bool(not files)
        raise OSError('Path is not valid: {0}'.format(path.path))

    def findNew(self, releases):
        """ Find any files that look "new", this means unsorted, not
        necessarily new files.
        
        :param releases: list of directories to look through
        :type releases: list filter
        :return: New files
        :rtype: filter
        """
        return filter(self.isNew, releases)

    def _genPath(self, filename):
        """ Generate a path from the basepath

        :param filename: File name
        :type filename: str
        :return: Full path to filename
        :rtype: str
        """
        return "{0}/{1}".format(self.basePath, filename)

    def findParentDir(self, path, dest=None, mtype=None):
        """ Find the parent path of the media folder supplied

        :param path: Base path to search from
        :type path: str
        :param dest: Optional default destination
        :type dest: str
        :param mtype: Optional default mediatype
        :type mtype: str
        :return: Found mediatype and destination
        :rtype: bool, bool

        """
        found = False
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
                        found = True
                if found: break
            if found: break
            
        if dest:
            # TODO move this to a separate method
            if not exists(dest):
                if self.config.getboolean('general', 'commit'):
                    mkdirp(dest)
                else:
                    log.info('Skipped creating directory: {0}'.format(dest))
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

    def getReleaseFiles(self, folder, filelist=[]):
        """ Get a list of files within the releases folder

        :param folder: Folder to look through
        :type folder: str
        :param filelist: Optional list of files to append to
        :return: files found under the folder path
        :rtype: list
        """
        if not exists(folder):
            raise OSError('Invalid path: {0}'.format(folder))
        [ map(filelist.append, [ join(root, f) for f in files ]) for root, dirs, files in walk(folder) ]
        return filelist

    def isLocked(self, filename):
        """ Check to see if a file is in a locked state (in use)

        :param filename: File to check
        :type filename: str
        :return: Locked status
        :rtype: bool
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
    This probably doesnt work very well under windows?

    :param path: Path to parse
    :type path: str
    :return List of path pieces
    :rtype: list
    """
    return normpath(abspath(path)).split(sep)[1:]

def mkdirp(dest):
    """ Emulate 'mkdir -p'

    :param dest: Path to create
    :type dest: str
    :raise OSError: Anything but already exists
    """
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

def isOpen(filepath):
    pids=listdir('/proc')
    for pid in sorted(pids):
        try:
            int(pid)
        except ValueError:
            continue
        fd_dir=join('/proc', pid, 'fd')
        for file in listdir(fd_dir):
            try:
                link=readlink(join(fd_dir, file))
            except OSError:
                continue
            print(pid, link) 